"""Repository management tasks powered by `invoke`.

More information on `invoke` can be found at http://www.pyinvoke.org/.
"""
# pylint: disable=import-outside-toplevel,too-many-locals
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from invoke import task

if TYPE_CHECKING:  # pragma: no cover
    from typing import Tuple

    from invoke import Context, Result


TOP_DIR = Path(__file__).parent.resolve()


def update_file(filename: Path, sub_line: "Tuple[str, str]", strip: str = None) -> None:
    """Utility function for tasks to read, update, and write files"""
    lines = [
        re.sub(sub_line[0], sub_line[1], line.rstrip(strip))
        for line in filename.read_text(encoding="utf8").splitlines()
    ]
    filename.write_text("\n".join(lines) + "\n", encoding="utf8")


@task(help={"version": "oteapi-optimade version to set"})
def setver(_, version=""):
    """Sets the oteapi-optimade version."""
    match = re.fullmatch(
        (
            r"v?(?P<version>[0-9]+(\.[0-9]+){2}"  # Major.Minor.Patch
            r"(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?"  # pre-release
            r"(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?)"  # build metadata
        ),
        version,
    )
    if not match:
        sys.exit(
            "Error: Please specify version as "
            "'Major.Minor.Patch(-Pre-Release+Build Metadata)' or "
            "'vMajor.Minor.Patch(-Pre-Release+Build Metadata)'"
        )
    version = match.group("version")

    update_file(
        TOP_DIR / "oteapi_optimade" / "__init__.py",
        (r'__version__ = (\'|").*(\'|")', f'__version__ = "{version}"'),
    )
    update_file(
        TOP_DIR / "tests" / "static" / "test_optimade_config.yml",
        (r"version: ('|\").*('|\")", f'version: "{version}"'),
    )

    print(f"Bumped version to {version}.")


@task(
    help={
        "pre-clean": "Remove the 'api_reference' sub directory prior to (re)creation.",
        "pre-commit": "Return a non-zero error code if changes were made.",
    }
)  # pylint: disable=too-many-branches
def create_api_reference_docs(context, pre_clean=False, pre_commit=False):
    """Create the API Reference in the documentation."""
    import os
    import shutil

    def write_file(full_path: Path, content: str) -> None:
        """Write file with `content` to `full_path`"""
        if full_path.exists():
            cached_content = full_path.read_text(encoding="utf8")
            if content == cached_content:
                del cached_content
                return
            del cached_content
        full_path.write_text(content, encoding="utf8")

    package_dir = TOP_DIR / "oteapi_optimade"
    docs_api_ref_dir = TOP_DIR / "docs" / "api_reference"

    unwanted_subdirs = ("__pycache__",)
    unwanted_files = ("__init__.py",)

    pages_template = 'title: "{name}"\n'
    md_template = "# {name}\n\n::: {py_path}\n"
    models_template = (
        md_template + f"{' ' * 4}rendering:\n{' ' * 6}show_if_no_docstring: true\n"
    )

    if docs_api_ref_dir.exists() and pre_clean:
        shutil.rmtree(docs_api_ref_dir, ignore_errors=True)
        if docs_api_ref_dir.exists():
            sys.exit(f"{docs_api_ref_dir} should have been removed!")
    docs_api_ref_dir.mkdir(exist_ok=True)

    write_file(
        full_path=docs_api_ref_dir / ".pages",
        content=pages_template.format(name="API Reference"),
    )

    for dirpath, dirnames, filenames in os.walk(package_dir):
        for unwanted_dir in unwanted_subdirs:
            if unwanted_dir in dirnames:
                # Avoid walking into or through unwanted directories
                dirnames.remove(unwanted_dir)

        relpath = Path(dirpath).relative_to(package_dir)

        if not (package_dir.name / relpath / "__init__.py").exists():
            # Avoid paths that are not included in the public Python API
            print("does not exist:", package_dir.name / relpath / "__init__.py")
            continue

        # Create `.pages`
        docs_sub_dir = docs_api_ref_dir / relpath
        docs_sub_dir.mkdir(exist_ok=True)
        print(docs_sub_dir)
        if str(relpath) != ".":
            write_file(
                full_path=docs_sub_dir / ".pages",
                content=pages_template.format(
                    name=str(relpath).rsplit("/", maxsplit=1)[-1]
                ),
            )

        # Create markdown files
        for filename in filenames:
            if re.match(r".*\.py$", filename) is None or filename in unwanted_files:
                # Not a Python file: We don't care about it!
                # Or filename is in the tuple of unwanted files:
                # We don't want it!
                continue

            basename = filename[: -len(".py")]
            py_path = (
                f"{package_dir.name}/{relpath}/{basename}".replace("/", ".")
                if str(relpath) != "."
                else f"{package_dir.name}/{basename}".replace("/", ".")
            )
            md_filename = filename.replace(".py", ".md")

            # For models we want to include EVERYTHING, even if it doesn't have a
            # doc-string
            template = models_template if str(relpath) == "models" else md_template

            write_file(
                full_path=docs_sub_dir / md_filename,
                content=template.format(name=basename, py_path=py_path),
            )

    if pre_commit:
        # Check if there have been any changes.
        # List changes if yes.
        if TYPE_CHECKING:  # pragma: no cover
            context: "Context" = context

        # NOTE: grep returns an exit code of 1 if it doesn't find anything
        # (which will be good in this case).
        # Concerning the weird last grep command see:
        # http://manpages.ubuntu.com/manpages/precise/en/man1/git-status.1.html
        result: "Result" = context.run(
            "git status --porcelain docs/api_reference | "
            "grep -E '^[? MARC][?MD]' || exit 0",
            hide=True,
        )
        if result.stdout:
            sys.exit(
                "The following files have been changed/added, please stage "
                f"them:\n\n{result.stdout}"
            )


@task
def create_docs_index(_):
    """Create the documentation index page from README.md"""
    readme = TOP_DIR / "README.md"
    docs_index = TOP_DIR / "docs" / "index.md"

    content = readme.read_text(encoding="utf8")

    replacement_mapping = [
        ("docs/", ""),
        ("(LICENSE)", "(LICENSE.md)"),
    ]

    for old, new in replacement_mapping:
        content = content.replace(old, new)

    docs_index.write_text(content, encoding="utf8")


# @task(
#     help={
#         "fail-fast": (
#             "Fail immediately if an error occurs. Otherwise, print and ignore all "
#             "non-critical errors."
#         ),
#     }
# )
# def update_deps(context, fail_fast=False):  # pylint: disable=too-many-branches
#     """Update dependencies in `pyproject.toml`."""
#     import tomlkit

#     if TYPE_CHECKING:  # pragma: no cover
#         context: "Context" = context

#     pyproject_path = TOP_DIR / "pyproject.toml"
#     pyproject = tomlkit.loads(pyproject_path.read_bytes())

#     py_version = re.match(
#         r"^.*(?P<version>3\.[0-9]+)$",
#         pyproject.get("project", {}).get("requires-python", ""),
#     ).group("version")

#     already_handled_packages = []
#     updated_packages = {}
#     dependencies = pyproject.get("project", {}).get("dependencies", [])
#     for optional_deps in (
#         pyproject.get("project", {}).get("optional-dependencies", {}).values()
#     ):
#         dependencies.extend(optional_deps)
#     for line in dependencies:
#         match = re.match(
#             r"^(?P<full_dependency>(?P<package>[a-zA-Z0-9-_]+)\S*) "
#             r"(?P<operator>>|<|<=|>=|==|!=|~=)"
#             r"(?P<version>[0-9]+(?:\.[0-9]+){0,2})$",
#             line,
#         )
#         if match is None:
#             msg = f"Could not parse package, operator, and version for line:\n  {line}"
#             if fail_fast:
#                 sys.exit(msg)
#             print(msg)
#         full_dependency_name = match.group("full_dependency")
#         package = match.group("package")
#         operator = match.group("operator")
#         version = match.group("version")

#         # Skip package if already handled
#         if package in already_handled_packages:
#             continue

#         out: "Result" = context.run(
#             f"pip index versions --python-version {py_version} {package}",
#             hide=True,
#         )
#         package_latest_version_line = out.stdout.split(sep="\n", maxsplit=1)[0]
#         match = re.match(
#             r"(?P<package>[a-zA-Z0-9-_]+) \((?P<version>[0-9]+(?:\.[0-9]+){0,2})\)",
#             package_latest_version_line,
#         )
#         if match is None:
#             msg = (
#                 "Could not parse package and version from 'pip index versions' output "
#                 f"for line:\n  {package_latest_version_line}"
#             )
#             if fail_fast:
#                 sys.exit(msg)
#             print(msg)

#         # Sanity check
#         if package != match.group("package"):
#             msg = (
#                 f"Package name parsed from pyproject.toml ({package!r}) does not match"
#                 " the name returned from 'pip index versions': "
#                 f"{match.group('package')!r}"
#             )
#             if fail_fast:
#                 sys.exit(msg)
#             print(msg)

#         latest_version = match.group("version").split(".")
#         for index, version_part in enumerate(version.split(".")):
#             if version_part != latest_version[index]:
#                 break
#         else:
#             already_handled_packages.append(package)
#             continue

#         # Update pyproject.toml
#         updated_version = ".".join(latest_version[: len(version.split("."))])
#         escaped_full_dependency_name = full_dependency_name.replace(
#             "[", "\["  # pylint: disable=anomalous-backslash-in-string
#         ).replace(
#             "]", "\]"  # pylint: disable=anomalous-backslash-in-string
#         )
#         update_file(
#             pyproject_path,
#             (
#                 rf'"{escaped_full_dependency_name} {operator}.*"',
#                 f'"{full_dependency_name} {operator}{updated_version}"',
#             ),
#         )
#         already_handled_packages.append(package)
#         updated_packages[full_dependency_name] = f"{operator}{updated_version}"

#     if updated_packages:
#         print(
#             "Successfully updated the following dependencies:\n"
#             + "\n".join(
#                 f"  {package} ({version})"
#                 for package, version in updated_packages.items()
#             )
#             + "\n"
#         )
#     else:
#         print("No dependency updates available.")

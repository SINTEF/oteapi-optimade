"""Pytest fixtures and configuration."""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def pytest_configure(config) -> None:  # pylint: disable=unused-argument
    """Method that runs before pytest collects tests, so no modules are imported."""
    import os
    from pathlib import Path

    cwd = Path(__file__).resolve().parent.resolve()
    os.environ["OPTIMADE_CONFIG_FILE"] = str(
        cwd / "static" / "test_optimade_config.yml"
    )


@pytest.fixture(scope="session")
def top_dir() -> "Path":
    """Return resolved Path object to the repository's top directory."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent.resolve()


@pytest.fixture(scope="session")
def static_files(top_dir: "Path") -> "Path":
    """Return Path object to the `static` folder."""
    return (top_dir / "tests" / "static").resolve()

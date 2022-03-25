"""Pytest fixtures and configuration."""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="session")
def top_dir() -> "Path":
    """Return resolved Path object to the repository's top directory."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent.resolve()


@pytest.fixture(scope="session")
def static_files(top_dir: "Path") -> "Path":
    """Return Path object to the `static` folder."""
    return (top_dir / "tests" / "static").resolve()

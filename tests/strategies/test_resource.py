"""Test `oteapi_optimade.strategies.resource` module.
Specifically the `OPTIMADEResourceStrategy` class.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from requests_mock import Mocker


@pytest.fixture()
def resource_config() -> dict[str, str]:
    """A resource config dictionary for test purposes."""
    return {
        "accessService": "optimade",
        "accessUrl": (
            "https://example.org/some/base/v0.1/optimade/v1/structures"
            '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
        ),
    }


@pytest.mark.parametrize(
    "session", [None, {"optimade_config": "content"}], ids=["None", "dict"]
)
def test_initialize(session: dict | None, resource_config: dict[str, str]) -> None:
    """Test the `initialize()` method."""
    from oteapi.models import SessionUpdate

    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    session_update = OPTIMADEResourceStrategy(resource_config).initialize(session)

    assert isinstance(session_update, SessionUpdate)
    assert {**session_update} == {}


def test_get_no_session(
    resource_config: dict[str, str], static_files: Path, requests_mock: Mocker
) -> None:
    """Test the `get()` method - session is `None`."""
    from optimade.adapters import Structure

    from oteapi_optimade.models.strategies.resource import OPTIMADEResourceSession
    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    sample_file = static_files / "optimade_response.json"
    requests_mock.get(resource_config["accessUrl"], content=sample_file.read_bytes())

    session = OPTIMADEResourceStrategy(resource_config).get()

    assert isinstance(session, OPTIMADEResourceSession)
    assert session.optimade_config is None
    assert session.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert session.optimade_resources
    for resource in session.optimade_resources:
        assert Structure(resource)


@pytest.mark.parametrize(
    ("accessService", "use_dlite"),
    [
        ("optimade+dlite", False),
        ("OPTIMADE+dlite", False),
        ("OPTiMaDe+dlite", False),
        ("optimade+DLite", False),
        ("OPTIMADE+DLite", False),
        ("OPTiMaDe+DLite", False),
        ("optimade", True),
        ("OPTIMADE", True),
        ("OPTiMaDe", True),
        ("optimade+dlite", True),
        ("OPTIMADE+dlite", True),
        ("OPTiMaDe+dlite", True),
        ("optimade+DLite", True),
        ("OPTIMADE+DLite", True),
        ("OPTiMaDe+DLite", True),
    ],
)
def test_use_dlite(
    resource_config: dict[str, str],
    static_files: Path,
    requests_mock: Mocker,
    accessService: str,
    use_dlite: bool,
) -> None:
    """Test the `get()` method - session is `None` and use_dlite is True."""
    from optimade.adapters import Structure
    from oteapi_dlite.utils import get_collection

    from oteapi_optimade.models.strategies.resource import OPTIMADEResourceSession
    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    sample_file = static_files / "optimade_response.json"
    requests_mock.get(resource_config["accessUrl"], content=sample_file.read_bytes())

    resource_config["accessService"] = accessService
    resource_config["configuration"] = {"use_dlite": use_dlite}

    session = OPTIMADEResourceStrategy(resource_config).initialize()
    session = OPTIMADEResourceStrategy(resource_config).get(session)

    assert isinstance(session, OPTIMADEResourceSession)
    assert session.optimade_config is None
    assert session.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert session.optimade_resources
    for resource in session.optimade_resources:
        assert Structure(resource)

    assert "collection_id" in session
    dlite_collection = get_collection(session)
    assert dlite_collection

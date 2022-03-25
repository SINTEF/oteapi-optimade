"""Test `oteapi_optimade.strategies.resource` module.
Specifically the `OPTIMADEResourceStrategy` class.
"""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional

    from requests_mock import Mocker


@pytest.fixture
def resource_config() -> dict[str, str]:
    """A resource config dictionary for test purposes."""
    return {
        "accessService": "optimade",
        "accessUrl": (
            "https://example.org/v1/structures"
            '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
        ),
    }


@pytest.mark.parametrize(
    "session", [None, {"optimade_config": "content"}], ids=["None", "dict"]
)
def test_initialize(session: "Optional[dict]", resource_config: dict[str, str]) -> None:
    """Test the `initialize()` method."""
    from oteapi.models import SessionUpdate

    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    session_update = OPTIMADEResourceStrategy(resource_config).initialize(session)

    assert isinstance(session_update, SessionUpdate)
    assert {**session_update} == {}


def test_get_no_session(
    resource_config: dict[str, str], static_files: "Path", requests_mock: "Mocker"
) -> None:
    """Test the `get()` method - session is `None`."""
    from optimade.adapters import Structure

    from oteapi_optimade.models.session import OPTIMADESession
    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    sample_file = static_files / "optimade_response.json"
    requests_mock.get(resource_config["accessUrl"], content=sample_file.read_bytes())

    session = OPTIMADEResourceStrategy(resource_config).get()

    assert isinstance(session, OPTIMADESession)
    assert session.optimade_config is None
    assert not session.optimade_errors
    assert not session.optimade_references
    assert session.optimade_structures
    for structure in session.optimade_structures:
        assert isinstance(structure, Structure)

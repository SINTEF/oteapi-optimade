"""Test `oteapi_optimade.strategies.resource` module.
Specifically the `OPTIMADEResourceStrategy` class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import sys
    from pathlib import Path

    if sys.version_info >= (3, 10):
        from typing import Literal
    else:
        from typing_extensions import Literal

    from requests_mock import Mocker


@pytest.fixture()
def resource_config() -> dict[str, str]:
    """A resource config dictionary for test purposes."""
    return {
        "resourceType": "optimade/structures",
        "accessService": "optimade",
        "accessUrl": (
            "https://example.org/some/base/v0.1/optimade/v1/structures"
            '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
        ),
    }


@pytest.mark.parametrize(
    "session", [None, {"optimade_config": {"version": "v1"}}], ids=["None", "dict"]
)
def test_initialize(session: dict | None, resource_config: dict[str, str]) -> None:
    """Test the `initialize()` method."""
    from oteapi.models import AttrDict

    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    if session:
        resource_config["configuration"] = session

    output = OPTIMADEResourceStrategy(resource_config).initialize()

    assert isinstance(output, AttrDict)
    assert {**output} == {}


def test_get_no_session(
    resource_config: dict[str, str], static_files: Path, requests_mock: Mocker
) -> None:
    """Test the `get()` method - no previous strategies have run
    (i.e., no session info has been added to `configuration`)."""
    from optimade.adapters import Structure

    from oteapi_optimade.models.strategies.resource import OPTIMADEResourceResult
    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    sample_file = static_files / "optimade_response.json"
    requests_mock.get(resource_config["accessUrl"], content=sample_file.read_bytes())

    output = OPTIMADEResourceStrategy(resource_config).get()

    assert isinstance(output, OPTIMADEResourceResult)
    assert output.optimade_config is None
    assert output.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert output.optimade_resources
    for resource in output.optimade_resources:
        assert Structure(resource)


@pytest.mark.parametrize("use_dlite", [True, False])
@pytest.mark.parametrize("accessService_root", ["optimade", "OPTIMADE", "OPTiMaDe"])
@pytest.mark.parametrize("accessService_appendix", ["", "+dlite", "+DLite"])
def test_use_dlite(
    resource_config: dict[str, str],
    static_files: Path,
    requests_mock: Mocker,
    accessService_root: Literal["optimade", "OPTIMADE", "OPTiMaDe"],
    accessService_appendix: Literal["+dlite", "+DLite"],
    use_dlite: Literal[True, False],
) -> None:
    """Test the `get()` method when `use_dlite` is set and for different valid accessService values."""
    from optimade.adapters import Structure
    from oteapi_dlite.utils import get_collection

    from oteapi_optimade.models.strategies.resource import OPTIMADEResourceResult
    from oteapi_optimade.strategies.resource import OPTIMADEResourceStrategy

    sample_file = static_files / "optimade_response.json"
    requests_mock.get(resource_config["accessUrl"], content=sample_file.read_bytes())

    resource_config["accessService"] = accessService_root + accessService_appendix
    resource_config["configuration"] = {"use_dlite": use_dlite}

    resource_config["configuration"].update(
        OPTIMADEResourceStrategy(resource_config).initialize()
    )
    output = OPTIMADEResourceStrategy(resource_config).get()

    assert isinstance(output, OPTIMADEResourceResult)
    assert output.optimade_config is None
    assert output.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert output.optimade_resources
    for resource in output.optimade_resources:
        assert Structure(resource)

    if use_dlite or "+dlite" in resource_config["accessService"].lower():
        assert "collection_id" in resource_config["configuration"]
        assert get_collection(
            collection_id=resource_config["configuration"]["collection_id"]
        ).get_labels()
    else:
        assert "collection_id" not in resource_config["configuration"]

"""Test `oteapi_optimade.dlite.parse` module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

    from dlite import Instance


@pytest.fixture(autouse=True)
def _use_local_entities(top_dir: Path, tmp_path: Path) -> None:
    """Use local entities."""
    import json

    import dlite
    import yaml

    entities_path = top_dir / "entities"

    # Create JSON files for the entities in a temporary directory
    for entity in entities_path.glob("*.y*ml"):
        entity_data = yaml.safe_load(entity.read_text())
        entity_json = tmp_path / f"{entity.stem}.json"
        entity_json.write_text(json.dumps(entity_data))

    # Add the temporary directory to the DLite storage paths
    dlite.storage_path.append(str(tmp_path / "*.json"))


def test_parse_nested_entities(static_files: Path) -> None:
    """Test parsing using the "original" entity with nested entities."""
    import json
    from datetime import datetime
    from enum import Enum

    from numpy import ndarray
    from optimade.adapters import Structure
    from oteapi.datacache import DataCache
    from oteapi_dlite.utils import get_collection

    from oteapi_optimade.dlite.parse import OPTIMADEDLiteParseStrategy
    from oteapi_optimade.models.custom_types import OPTIMADEUrl

    url = OPTIMADEUrl(
        "https://example.org/some/base/v0.1/optimade/v1/structures"
        '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
    )
    config = {
        "entity": "http://onto-ns.com/meta/1.2.0/OPTIMADEStructure",
        "parserType": "parser/OPTIMADE/DLite",
        "configuration": {
            "mediaType": "application/vnd.OPTIMADE+DLite",
            "downloadUrl": url,
            "datacache_config": {
                "expireTime": 60 * 60 * 24,
                "tag": "optimade",
                "accessKey": url,
            },
        },
    }

    cache = DataCache(config["configuration"]["datacache_config"])
    sample_file = static_files / "optimade_response.json"
    response_json: dict[str, Any] = json.loads(sample_file.read_bytes())
    cache.add(
        {
            "status_code": 200,
            "ok": True,
            "json": response_json,
        }
    )

    config["configuration"].update(OPTIMADEDLiteParseStrategy(config).initialize())
    config["configuration"].update(OPTIMADEDLiteParseStrategy(config).get())

    dlite_collection = get_collection(
        collection_id=config["configuration"]["collection_id"]
    )

    assert len(list(dlite_collection.get_labels())) == len(response_json["data"])

    for structure in response_json["data"]:
        optimade_structure = Structure(structure)
        dlite_collection_labels = list(dlite_collection.get_labels())

        # The structure `id` is used as the label for the instance in the DLite
        # collection
        assert optimade_structure.id in dlite_collection_labels

        dlite_structure: Instance = dlite_collection[optimade_structure.id]

        ## Go over other top-level non-container keys in the OPTIMADE structure
        assert dlite_structure.type == optimade_structure.type

        ## attributes

        # Avoid attributes with special model values for now
        model_values = ("assemblies", "species")

        for field in optimade_structure.attributes.__class__.model_fields:
            if field in model_values:
                continue

            expected_value = getattr(optimade_structure.attributes, field)

            # Ensure expected values come in the right format
            if expected_value and isinstance(expected_value, list):
                # We expect that all internal types in the list are the same
                if isinstance(expected_value[0], Enum):
                    expected_value = [value.value for value in expected_value]
                if isinstance(expected_value[0], datetime):
                    expected_value = [
                        value.isoformat(sep=" ") for value in expected_value
                    ]

            if expected_value is None:
                if field == "space_group_symmetry_operations_xyz":
                    expected_value = []
                elif field == "space_group_it_number":
                    expected_value = 0

            if isinstance(expected_value, Enum):
                expected_value = expected_value.value
            if isinstance(expected_value, datetime):
                expected_value = expected_value.isoformat(sep=" ")

            dlite_value = getattr(dlite_structure.attributes, field)

            # Convert NumPy NDArrays to lists
            if isinstance(dlite_value, ndarray):
                dlite_value = dlite_value.tolist()
            # Convert string "None" values to actual Python None values
            if isinstance(dlite_value, str) and dlite_value == "None":
                dlite_value = None

            assert dlite_value == expected_value, f"Field: {field}"

        # Special attributes
        for field in model_values:
            # The model value fields are lists of models
            expected_value = getattr(optimade_structure.attributes, field)
            if expected_value is None:
                assert getattr(dlite_structure.attributes, field) is None
                continue

            assert isinstance(expected_value, list)
            assert isinstance(getattr(dlite_structure.attributes, field), ndarray)

            for i, entry in enumerate(getattr(dlite_structure.attributes, field)):
                for sub_field in getattr(optimade_structure.attributes, field)[
                    0
                ].__class__.model_fields:
                    expected_sub_value = getattr(expected_value[i], sub_field)
                    dlite_sub_value = getattr(entry, sub_field)

                    # Ensure expected values come in the right format
                    if expected_sub_value and isinstance(expected_sub_value, list):
                        # We expect that all internal types in the list are the same
                        if isinstance(expected_sub_value[0], Enum):
                            expected_sub_value = [
                                value.value for value in expected_sub_value
                            ]
                        if isinstance(expected_sub_value[0], datetime):
                            expected_sub_value = [
                                value.isoformat(sep=" ") for value in expected_sub_value
                            ]

                    if isinstance(expected_sub_value, Enum):
                        expected_sub_value = expected_sub_value.value
                    if isinstance(expected_sub_value, datetime):
                        expected_sub_value = expected_sub_value.isoformat(sep=" ")

                    # Convert NumPy NDArrays to lists
                    if isinstance(dlite_sub_value, ndarray):
                        dlite_sub_value = dlite_sub_value.tolist()
                    # Convert string "None" values to actual Python None values
                    if isinstance(dlite_sub_value, str) and dlite_sub_value == "None":
                        dlite_sub_value = None

                    # If an optional field is not present in the data, it will be None.
                    # In DLite it will always be instantiated with the default values.
                    # This is an issue with a shaped properties.
                    # Here we update the expected_sub_value accordingly, with respect
                    # to specific known optional sub-fields.

                    # species.mass
                    if (
                        field == "species"
                        and sub_field == "mass"
                        and expected_sub_value is None
                    ):
                        expected_sub_value = [0.0] * len(
                            expected_value[i].chemical_symbols
                        )

                    # species.attached
                    if (
                        field == "species"
                        and sub_field == "attached"
                        and expected_sub_value is None
                    ):
                        expected_sub_value = []

                    # species.nattached
                    if (
                        field == "species"
                        and sub_field == "nattached"
                        and expected_sub_value is None
                    ):
                        expected_sub_value = []

                    assert dlite_sub_value == (
                        expected_sub_value or []
                    ), f"Field: {field}, sub-field: {sub_field}"


def test_parse_single_entity(static_files: Path) -> None:
    """Test parsing using the single entity for a resource."""
    import json
    from datetime import datetime
    from enum import Enum

    from numpy import ndarray
    from optimade.models import StructureResource
    from oteapi.datacache import DataCache
    from oteapi_dlite.utils import get_collection

    from oteapi_optimade import parse_assemblies, parse_species
    from oteapi_optimade.dlite.parse import OPTIMADEDLiteParseStrategy
    from oteapi_optimade.models.custom_types import OPTIMADEUrl

    url = OPTIMADEUrl(
        "https://example.org/some/base/v0.1/optimade/v1/structures"
        '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
    )
    config = {
        "entity": "http://onto-ns.com/meta/1.2.0/OPTIMADEStructureResource",
        "parserType": "parser/OPTIMADE/DLite",
        "configuration": {
            "mediaType": "application/vnd.OPTIMADE+DLite",
            "downloadUrl": url,
            "datacache_config": {
                "expireTime": 60 * 60 * 24,
                "tag": "optimade",
                "accessKey": url,
            },
        },
    }

    cache = DataCache(config["configuration"]["datacache_config"])
    sample_file = static_files / "optimade_response.json"
    response_json: dict[str, Any] = json.loads(sample_file.read_bytes())
    cache.add(
        {
            "status_code": 200,
            "ok": True,
            "json": response_json,
        }
    )

    config["configuration"].update(OPTIMADEDLiteParseStrategy(config).initialize())
    config["configuration"].update(OPTIMADEDLiteParseStrategy(config).get())

    dlite_collection = get_collection(
        collection_id=config["configuration"]["collection_id"]
    )

    assert len(list(dlite_collection.get_labels())) == len(response_json["data"])

    for structure in response_json["data"]:
        optimade_structure = StructureResource(**structure)
        dlite_collection_labels = list(dlite_collection.get_labels())

        # The structure `id` is used as the label for the instance in the DLite
        # collection
        assert optimade_structure.id in dlite_collection_labels

        dlite_structure: Instance = dlite_collection[optimade_structure.id]

        ## Go over other top-level non-container keys in the OPTIMADE structure
        assert dlite_structure.type == optimade_structure.type

        ## attributes

        # Avoid attributes with special model values for now
        model_values = ("assemblies", "species")

        for field in optimade_structure.attributes.__class__.model_fields:
            if field in model_values:
                continue

            expected_value = getattr(optimade_structure.attributes, field)

            # Ensure expected values come in the right format
            if expected_value and isinstance(expected_value, list):
                # We expect that all internal types in the list are the same
                if isinstance(expected_value[0], Enum):
                    expected_value = [value.value for value in expected_value]
                if isinstance(expected_value[0], datetime):
                    expected_value = [
                        value.isoformat(sep=" ") for value in expected_value
                    ]

            if expected_value is None:
                if field == "space_group_symmetry_operations_xyz":
                    expected_value = []
                elif field == "space_group_it_number":
                    expected_value = 0

            if isinstance(expected_value, Enum):
                expected_value = expected_value.value
            if isinstance(expected_value, datetime):
                expected_value = expected_value.isoformat(sep=" ")

            dlite_value = getattr(dlite_structure, field)

            # Convert NumPy NDArrays to lists
            if isinstance(dlite_value, ndarray):
                dlite_value = dlite_value.tolist()
            # Convert string "None" values to actual Python None values
            if isinstance(dlite_value, str) and dlite_value == "None":
                dlite_value = None

            assert dlite_value == expected_value, f"Field: {field}"

        # Special attributes
        for field in model_values:
            # The model value fields are lists of models
            expected_value = getattr(optimade_structure.attributes, field)
            if expected_value is None:
                assert getattr(dlite_structure, field, None) is None
                continue

            # Parse field from the DLite structure
            if field == "assemblies":
                parsed_value = parse_assemblies(dlite_structure)
            elif field == "species":
                parsed_value = parse_species(dlite_structure)
            else:
                pytest.fail(f"Unknown model value field: {field}")

            assert isinstance(expected_value, list)
            assert isinstance(parsed_value, list)

            for i, entry in enumerate(parsed_value):
                for sub_field in getattr(optimade_structure.attributes, field)[
                    0
                ].__class__.model_fields:
                    expected_sub_value = getattr(expected_value[i], sub_field)
                    dlite_sub_value = entry.get(sub_field)

                    # Ensure expected values come in the right format
                    if expected_sub_value and isinstance(expected_sub_value, list):
                        # We expect that all internal types in the list are the same
                        if isinstance(expected_sub_value[0], Enum):
                            expected_sub_value = [
                                value.value for value in expected_sub_value
                            ]
                        if isinstance(expected_sub_value[0], datetime):
                            expected_sub_value = [
                                value.isoformat(sep=" ") for value in expected_sub_value
                            ]

                    if isinstance(expected_sub_value, Enum):
                        expected_sub_value = expected_sub_value.value
                    if isinstance(expected_sub_value, datetime):
                        expected_sub_value = expected_sub_value.isoformat(sep=" ")

                    # Convert string "None" values to actual Python None values
                    if isinstance(dlite_sub_value, str) and dlite_sub_value == "None":
                        dlite_sub_value = None

                    assert (
                        dlite_sub_value == expected_sub_value or dlite_sub_value == []
                    ), f"Field: {field}, sub-field: {sub_field}"

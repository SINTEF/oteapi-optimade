"""Utility and helper functions."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

import dlite

if TYPE_CHECKING:  # pragma: no cover
    import sys
    from typing import Any

    if sys.version_info >= (3, 9, 1):
        from typing import Literal
    else:
        from typing_extensions import Literal  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


def _check_correct_entity(
    instance: dlite.Instance | dict[str, Any],
    entity_name: Literal["OPTIMADEStructure", "OPTIMADEStructureResource"],
) -> bool:
    """Check the given entity is the desired entity."""
    if isinstance(instance, dlite.Instance):
        if instance.is_meta:
            raise ValueError(
                f"Entity is a meta entity, it should be an instance (of {entity_name})."
            )
        uri = instance.meta.uri
    elif isinstance(instance, dict):
        uri = instance.get("meta")
    else:
        raise TypeError(f"Unsupported entity type: {type(instance)}")

    if not uri:
        raise ValueError("Entity does not have a meta URI.")

    return bool(
        re.match(
            rf"http://onto-ns\.com/meta/[0-9]+(\.[0-9]+)?(\.[0-9]+)?/{entity_name}", uri
        )
    )


def parse_species(instance: dlite.Instance | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse species properties from the OPTIMADEStructureResource entity into "proper" OPT
    StructureResource Species."""
    if not _check_correct_entity(instance, "OPTIMADEStructureResource"):
        raise ValueError(
            "Entity for the instance is not an OPTIMADEStructureResource entity."
        )

    if isinstance(instance, dlite.Instance):
        instance = instance.asdict(single=True)

    if not isinstance(instance, dict):
        raise TypeError("Entity instance is not a dictionary.")

    species: list[dict[str, Any]] = []

    for index in range(instance["dimensions"]["nspecies"]):
        # Required fields
        new_species = {
            "name": instance["properties"]["species_name"][index],
            "chemical_symbols": instance["properties"]["species_chemical_symbols"][
                index
            ].split(","),
            "concentration": [
                float(_)
                for _ in instance["properties"]["species_concentration"][index].split(
                    ","
                )
            ],
        }

        # Optional fields
        if mass := instance["properties"]["species_mass"][index]:
            new_species["mass"] = [float(_) for _ in mass.split(",")]

        if original_name := instance["properties"]["species_original_name"][index]:
            new_species["original_name"] = original_name

        if attached := instance["properties"]["species_attached"][index]:
            new_species["attached"] = attached.split(",")

            if "species_nattached" not in instance["properties"]:
                raise ValueError(
                    "species_attached is present, but species_nattached is missing."
                )

            new_species["nattached"] = [
                int(_)
                for _ in instance["properties"]["species_nattached"][index].split(",")
            ]

        species.append(new_species)

    return species


def parse_assemblies(instance: dlite.Instance | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse assemblies properties from the OPTIMADEStructureResource entity into "proper" OPT
    StructureResource 'Assembly's."""
    if not _check_correct_entity(instance, "OPTIMADEStructureResource"):
        raise ValueError(
            "Entity for the instance is not an OPTIMADEStructureResource entity."
        )

    if isinstance(instance, dlite.Instance):
        instance = instance.asdict(single=True)

    if not isinstance(instance, dict):
        raise TypeError("Entity instance is not a dictionary.")

    assemblies: list[dict[str, Any]] = []

    for index in range(instance["dimensions"]["nassemblies"]):
        assemblies.append(
            {
                "sites_in_groups": [
                    [int(_) for _ in group.split(",")]
                    for group in instance["properties"]["assembly_sites_in_groups"][
                        index
                    ].split(";")
                ],
                "group_probabilities": [
                    float(_)
                    for _ in instance["properties"]["assembly_group_probabilities"][
                        index
                    ].split(",")
                ],
            }
        )

    return assemblies

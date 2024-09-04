"""OTEAPI strategy for parsing OPTIMADE structure resources to DLite instances."""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

import dlite
from optimade.models import Response as OPTIMADEResponse
from optimade.models import (
    StructureResource,
    StructureResponseMany,
    StructureResponseOne,
    Success,
)
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEDLiteParseConfig, OPTIMADEParseResult
from oteapi_optimade.strategies.parse import OPTIMADEParseStrategy

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


LOGGER = logging.getLogger(__name__)


@dataclass
class OPTIMADEDLiteParseStrategy:
    """Parse strategy for JSON.

    **Implements strategies**:

    - `("parserType", "parser/OPTIMADE/DLite")`

    """

    parse_config: OPTIMADEDLiteParseConfig

    def initialize(self) -> DLiteSessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        return DLiteSessionUpdate(
            collection_id=get_collection(
                collection_id=self.parse_config.configuration.collection_id
            ).uuid
        )

    def get(self) -> OPTIMADEParseResult:
        """Request and parse an OPTIMADE response using OPT.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Configuration values provided in `resource_config.configuration` take
        precedence over the derived values from `downloadUrl`.

        Workflow:

        1. Request OPTIMADE response.
        2. Parse as an OPTIMADE Python tools (OPT) pydantic response model.

        ---

        The OPTIMADE Structure needs to be parsed into DLite instances inside-out,
        meaning the most nested data structures must first be parsed, and then the ones
        1 layer up and so on until the most upper layer can be parsed.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        generic_parse_config = self.parse_config.model_copy(
            update={
                "parserType": self.parse_config.parserType.replace("/dlite", ""),
                "configuration": self.parse_config.configuration.model_copy(
                    update={
                        "mediaType": self.parse_config.configuration.get(
                            "mediaType", ""
                        ).replace("+dlite", "+json")
                    }
                ),
            }
        ).model_dump(exclude_unset=True, exclude_defaults=True)
        generic_parse_result = OPTIMADEParseStrategy(generic_parse_config).get()

        OPTIMADEStructure = dlite.get_instance(str(self.parse_config.entity))

        single_entity = "OPTIMADEStructureResource" in OPTIMADEStructure.uri

        if not single_entity:
            nested_entity_mapping: dict[str, dlite.Instance] = self._get_nested_entity(
                OPTIMADEStructure
            )

        if not (
            generic_parse_result.optimade_response
            and generic_parse_result.optimade_response_model
        ):
            base_error_message = (
                "Could not retrieve response from OPTIMADE parse strategy."
            )
            LOGGER.error(
                "%s\n"
                "optimade_response=%r\n"
                "optimade_response_model=%r\n"
                "session fields=%r",
                base_error_message,
                generic_parse_result.get("optimade_response"),
                generic_parse_result.get("optimade_response_model"),
                list(generic_parse_result),
            )
            raise OPTIMADEParseError(base_error_message)

        optimade_response_model_module, optimade_response_model_name = (
            generic_parse_result.optimade_response_model
        )

        # Parse response using the provided model
        try:
            optimade_response_model: type[OPTIMADEResponse] = getattr(
                importlib.import_module(optimade_response_model_module),
                optimade_response_model_name,
            )
            optimade_response = optimade_response_model(
                **generic_parse_result.optimade_response
            )
        except (ImportError, AttributeError) as exc:
            base_error_message = "Could not import the response model."
            LOGGER.error(
                "%s\n"
                "ImportError: %s\n"
                "optimade_response_model_module=%r\n"
                "optimade_response_model_name=%r",
                base_error_message,
                exc,
                optimade_response_model_module,
                optimade_response_model_name,
            )
            raise OPTIMADEParseError(base_error_message) from exc
        except ValidationError as exc:
            base_error_message = "Could not validate the response model."
            LOGGER.error(
                "%s\n"
                "ValidationError: %s\n"
                "optimade_response_model_module=%r\n"
                "optimade_response_model_name=%r",
                base_error_message,
                exc,
                optimade_response_model_module,
                optimade_response_model_name,
            )
            raise OPTIMADEParseError(base_error_message) from exc

        # Currently, only "structures" entries are supported and handled
        if isinstance(optimade_response, StructureResponseMany):
            structures: list[StructureResource] = [
                (
                    StructureResource(**entry)
                    if isinstance(entry, dict)
                    else entry.model_copy(deep=True)
                )
                for entry in optimade_response.data
            ]

        elif isinstance(optimade_response, StructureResponseOne):
            structures = (
                [
                    (
                        StructureResource(**optimade_response.data)
                        if isinstance(optimade_response.data, dict)
                        else optimade_response.data.model_copy(deep=True)
                    )
                ]
                if optimade_response.data is not None
                else []
            )

        elif isinstance(optimade_response, Success):
            if isinstance(optimade_response.data, dict):
                structures = [StructureResource(**optimade_response.data)]
            elif isinstance(optimade_response.data, BaseModel):
                structures = [StructureResource(**optimade_response.data.model_dump())]
            elif isinstance(optimade_response.data, list):
                structures = [
                    (
                        StructureResource(**entry)
                        if isinstance(entry, dict)
                        else StructureResource(**entry.model_dump())
                    )
                    for entry in optimade_response.data
                ]
            elif optimade_response.data is None:
                structures = []
            else:
                LOGGER.error(
                    "Could not determine what to do with `data`. Type %s.",
                    type(optimade_response.data),
                )
                raise OPTIMADEParseError("Could not parse `data` entry in response.")

        else:
            LOGGER.error(
                "Got currently unsupported response type %s. Only structures are "
                "supported.",
                optimade_response_model_name,
            )
            raise OPTIMADEParseError(
                "The DLite OPTIMADE Parser currently only supports structures entities."
            )

        if not structures:
            LOGGER.warning("No structures found in the response.")
            return generic_parse_result

        # DLite-fy OPTIMADE structures
        dlite_collection = get_collection(
            collection_id=self.parse_config.configuration.collection_id
        )

        for structure in structures:
            new_structure_attributes: dict[str, Any] = {}
            single_entity_dimensions: dict[str, int] = {
                "nassemblies": 0,
                "nspecies": 0,
            }

            ## For OPTIMADEStructure (multiple) entities
            # Most inner layer: assemblies & species
            if structure.attributes.assemblies:
                if single_entity:
                    single_entity_dimensions["nassemblies"] = len(
                        structure.attributes.assemblies
                    )
                    new_structure_attributes.update(
                        {
                            "assemblies_sites_in_groups": [],
                            "assemblies_group_probabilities": [],
                        }
                    )
                else:
                    new_structure_attributes["assemblies"] = []

                for assembly in structure.attributes.assemblies:
                    if single_entity:
                        new_structure_attributes["assemblies_sites_in_groups"].append(
                            ";".join(
                                [
                                    ",".join(str(_) for _ in group)
                                    for group in assembly.sites_in_groups
                                ]
                            )
                        )
                        new_structure_attributes[
                            "assemblies_group_probabilities"
                        ].append(",".join(str(_) for _ in assembly.group_probabilities))
                    else:
                        if "attributes.assemblies" not in nested_entity_mapping:
                            LOGGER.error(
                                "Could not find entity for 'attributes.assemblies'.\nnested_entity_mapping=%r",
                                nested_entity_mapping,
                            )
                            raise OPTIMADEParseError(
                                "Could not find entity for 'attributes.assemblies'."
                            )

                        dimensions = {
                            "ngroups": len(assembly.group_probabilities),
                            "nsites": len(assembly.sites_in_groups),
                        }
                        new_structure_attributes["assemblies"].append(
                            nested_entity_mapping["attributes.assemblies"](
                                dimensions=dimensions, properties=assembly.model_dump()
                            )
                        )

            if structure.attributes.species:
                if single_entity:
                    single_entity_dimensions["nspecies"] = len(
                        structure.attributes.species
                    )
                    new_structure_attributes.update(
                        {
                            "species_name": [],
                            "species_chemical_symbols": [],
                            "species_concentration": [],
                            "species_mass": [],
                            "species_original_name": [],
                            "species_attached": [],
                            "species_nattached": [],
                        }
                    )
                else:
                    new_structure_attributes["species"] = []

                for species in structure.attributes.species:
                    if single_entity:
                        new_structure_attributes["species_name"].append(species.name)
                        new_structure_attributes["species_chemical_symbols"].append(
                            ",".join(species.chemical_symbols)
                        )
                        new_structure_attributes["species_concentration"].append(
                            ",".join(str(_) for _ in species.concentration)
                        )
                        new_structure_attributes["species_mass"].append(
                            ",".join(str(_) for _ in (species.mass or []))
                        )
                        new_structure_attributes["species_original_name"].append(
                            species.original_name or ""
                        )
                        new_structure_attributes["species_attached"].append(
                            ",".join(species.attached or [])
                        )
                        new_structure_attributes["species_nattached"].append(
                            ",".join(str(_) for _ in (species.nattached or []))
                        )
                    else:
                        if "attributes.species" not in nested_entity_mapping:
                            LOGGER.error(
                                "Could not find entity for 'attributes.species'.\nnested_entity_mapping=%r",
                                nested_entity_mapping,
                            )
                            raise OPTIMADEParseError(
                                "Could not find entity for 'attributes.species'."
                            )

                        dimensions = {
                            "nelements": len(species.chemical_symbols),
                            "nattached_elements": len(species.attached or []),
                        }
                        new_structure_attributes["species"].append(
                            nested_entity_mapping["attributes.species"](
                                dimensions=dimensions,
                                properties=species.model_dump(exclude_none=True),
                            )
                        )

            # Attributes
            new_structure_attributes.update(
                structure.attributes.model_dump(
                    exclude={
                        "species",
                        "assemblies",
                        "nelements",
                        "nsites",
                        "structure_features",
                    },
                    exclude_unset=True,
                    exclude_defaults=True,
                    exclude_none=True,
                )
            )
            for key in list(new_structure_attributes):
                if key.startswith("_"):
                    new_structure_attributes.pop(key)

            # Structure features values are Enum values, so we need to convert them to
            # their string (true) values
            new_structure_attributes["structure_features"] = [
                _.value for _ in structure.attributes.structure_features
            ]

            if single_entity:
                new_structure_attributes["id"] = structure.id
                new_structure_attributes["type"] = structure.type

                new_structure = OPTIMADEStructure(
                    dimensions={
                        "nelements": structure.attributes.nelements or 0,
                        "dimensionality": 3,
                        "nsites": structure.attributes.nsites or 0,
                        "nstructure_features": len(
                            structure.attributes.structure_features
                        ),
                        **single_entity_dimensions,
                    },
                    properties=new_structure_attributes,
                )
            else:
                if "attributes" not in nested_entity_mapping:
                    LOGGER.error(
                        "Could not find entity for 'attributes'.\nnested_entity_mapping=%r",
                        nested_entity_mapping,
                    )
                    raise OPTIMADEParseError("Could not find entity for 'attributes'.")

                new_structure = OPTIMADEStructure(
                    dimensions={},
                    properties={
                        "attributes": nested_entity_mapping["attributes"](
                            dimensions={
                                "nelements": structure.attributes.nelements or 0,
                                "dimensionality": 3,
                                "nsites": structure.attributes.nsites or 0,
                                "nspecies": (
                                    len(structure.attributes.species)
                                    if structure.attributes.species
                                    else 0
                                ),
                                "nstructure_features": len(
                                    structure.attributes.structure_features
                                ),
                            },
                            properties=new_structure_attributes,
                        ),
                        "type": structure.type,
                        "id": structure.id,
                    },
                )

            dlite_collection.add(label=structure.id, inst=new_structure)

        update_collection(collection=dlite_collection)

        return generic_parse_result

    def _get_nested_entity(self, entity: dlite.Instance) -> dict[str, dlite.Instance]:
        """Get nested entity from DLite instance."""
        nested_entities: dict[str, dlite.Instance] = {}

        for prop in entity.properties["properties"]:
            if prop.type == "ref":
                nested_entities[prop.name] = dlite.get_instance(prop.ref)

        for name, nested_entity in tuple(nested_entities.items()):
            futher_nested_entities = self._get_nested_entity(nested_entity)

            for nested_name, further_nested_entity in futher_nested_entities.items():
                nested_entities[f"{name}.{nested_name}"] = further_nested_entity

        return nested_entities

"""OTEAPI strategy for parsing OPTIMADE structure resources to DLite instances."""

from __future__ import annotations

import json
import logging
import sys
from typing import TYPE_CHECKING, Annotated, Optional, Union

if sys.version_info >= (3, 9, 1):
    from typing import Literal
else:
    from typing_extensions import Literal  # type: ignore[assignment]

import dlite
from optimade.models import ReferenceResource, StructureResource
from oteapi.datacache import DataCache
from oteapi.models import (
    AttrDict,
    DataCacheConfig,
    HostlessAnyUrl,
    ParserConfig,
    ResourceConfig,
)
from oteapi.plugins import create_strategy
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import BeforeValidator, Field, ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

OPTIMADEResource = Union[ReferenceResource, StructureResource]
"""Alias type for an OPTIMADE resource type."""

optimade_resources: dict[str, type[ReferenceResource | StructureResource]] = {
    "references": ReferenceResource,
    "structures": StructureResource,
}
"""Tuple of OPTIMADE resource types."""


LOGGER = logging.getLogger(__name__)


class OPTIMADEResourceDLiteConfig(AttrDict):
    """Strategy-specific configuration for the 'parser/optimade/resources' strategy."""

    downloadUrl: Annotated[
        Optional[HostlessAnyUrl],
        Field(description=ResourceConfig.model_fields["downloadUrl"].description),
    ] = None

    mediaType: Annotated[
        Optional[
            Literal[
                "application/vnd.optimade+json",
                "application/vnd.optimade",
                "application/json",
            ]
        ],
        Field(description=ResourceConfig.model_fields["mediaType"].description),
    ] = None

    datacache_config: Annotated[
        DataCacheConfig,
        Field(description="DataCache configuration for data retrieval."),
    ] = DataCacheConfig()

    parsed_data_key: Annotated[
        str,
        Field(description="Key to the parsed data stored in the DataCache."),
    ] = "optimade_resources"


class OPTIMADEResourceDLiteParserConfig(ParserConfig):
    """Parser config for the 'parser/optimade/resources' strategy."""

    parserType: Annotated[
        Literal[
            "parser/optimade/resources/dlite",
            "parser/optimade/structures/dlite",
            "parser/optimade/references/dlite",
        ],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(description=ParserConfig.model_fields["parserType"].description),
    ]

    configuration: Annotated[
        OPTIMADEResourceDLiteConfig,
        Field(description=ParserConfig.model_fields["configuration"].description),
    ] = OPTIMADEResourceDLiteConfig()


@dataclass
class OPTIMADEResourceDLiteParseStrategy:
    """Parse strategy for an OPTIMADE Entry Resource using DLite.

    **Implements strategies**:

    - `("parserType", "parser/OPTIMADE/resources/DLite")`
    - `("parserType", "parser/OPTIMADE/references/DLite")`
    - `("parserType", "parser/OPTIMADE/structures/DLite")`

    """

    parse_config: OPTIMADEResourceDLiteParserConfig

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

    def get(self) -> DLiteSessionUpdate:
        """Request and parse an OPTIMADE response using OPT.

        The OPTIMADE Structure needs to be parsed into DLite instances inside-out,
        meaning the most nested data structures must first be parsed, and then the ones
        1 layer up and so on until the most upper layer can be parsed.

        Unless using the single entity `OPTIMADEStructureResource`, where the nested
        values are flattened into the main entity.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        config = self.parse_config.configuration

        # Retrieve data
        cache = DataCache(config.datacache_config.model_copy(deep=True))
        if (
            config.datacache_config.accessKey
            and config.datacache_config.accessKey in cache
        ):
            data: Any = cache.get(config.datacache_config.accessKey)
        elif config.downloadUrl and config.downloadUrl in cache:
            data = cache.get(config.downloadUrl)
        elif config.downloadUrl:
            download_config = config.model_copy(deep=True)
            download_output = create_strategy("download", download_config).get()
            data = cache.get(download_output("key"))
        else:
            raise OPTIMADEParseError(
                "No download URL provided and could not find data in the cache."
            )

        if isinstance(data, (str, bytes)):
            data = json.loads(data)

        if not isinstance(data, (dict, list)):
            raise OPTIMADEParseError(
                f"Expected data to be a dict or list, got {type(data)} instead."
            )

        # Determine resource type
        explicit_resource_type = self._get_explicit_resource_type()

        if explicit_resource_type is None:
            datum = data if isinstance(data, dict) else data[0]
            for resource_class in optimade_resources.values():
                try:
                    resource_class(**datum)
                except ValidationError:
                    pass
                else:
                    explicit_resource_type = resource_class
                    break
            else:
                LOGGER.error("Could not determine resource type from data: %r", data)
                raise OPTIMADEParseError("Could not determine resource type from data.")

        if not isinstance(explicit_resource_type, optimade_resources["structures"]):
            LOGGER.error(
                "Currently only 'structures' resources are supported. Got %s.",
                explicit_resource_type,
            )
            raise OPTIMADEParseError(
                "Currently only 'structures' resources are supported."
            )

        # Parse data
        if isinstance(data, dict):
            data = [data]

        resources: list[OPTIMADEResource] = []

        for entry in data:
            try:
                resources.append(explicit_resource_type(**entry))
            except ValidationError as exc:
                LOGGER.error(
                    "Could not parse entry as %s: %r", explicit_resource_type, entry
                )
                raise OPTIMADEParseError(
                    f"Could not parse entry as {explicit_resource_type.__name__!r}."
                ) from exc

        OPTIMADEStructure = dlite.get_instance(str(self.parse_config.entity))

        single_entity = (
            OPTIMADEStructure.uri.rstrip("/")
            .rstrip("#")
            .endswith("/OPTIMADEStructureResource")
        )

        if not single_entity:
            nested_entity_mapping: dict[str, dlite.Instance] = self._get_nested_entity(
                OPTIMADEStructure
            )

        if not data:
            LOGGER.warning("No data found in the response.")
            return DLiteSessionUpdate(collection_id=config.collection_id)

        # DLite-fy OPTIMADE structures
        dlite_collection = get_collection(collection_id=config.collection_id)

        for resource in resources:
            if not isinstance(resource, optimade_resources["structures"]):
                LOGGER.error(
                    "Currently only 'structures' resources are supported. Got %s.",
                    type(resource),
                )
                raise OPTIMADEParseError(
                    "Currently only 'structures' resources are supported."
                )

            # Structures
            new_structure_attributes: dict[str, Any] = {}
            single_entity_dimensions: dict[str, int] = {
                "nassemblies": 0,
                "nspecies": 0,
            }

            ## For OPTIMADEStructure (multiple) entities
            # Most inner layer: assemblies & species
            if resource.attributes.assemblies:
                if single_entity:
                    single_entity_dimensions["nassemblies"] = len(
                        resource.attributes.assemblies
                    )
                    new_structure_attributes.update(
                        {
                            "assemblies_sites_in_groups": [],
                            "assemblies_group_probabilities": [],
                        }
                    )
                else:
                    new_structure_attributes["assemblies"] = []

                for assembly in resource.attributes.assemblies:
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

            if resource.attributes.species:
                if single_entity:
                    single_entity_dimensions["nspecies"] = len(
                        resource.attributes.species
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

                for species in resource.attributes.species:
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
                resource.attributes.model_dump(
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
                _.value for _ in resource.attributes.structure_features
            ]

            if single_entity:
                new_structure_attributes["id"] = resource.id
                new_structure_attributes["type"] = resource.type

                new_structure = OPTIMADEStructure(
                    dimensions={
                        "nelements": resource.attributes.nelements or 0,
                        "dimensionality": 3,
                        "nsites": resource.attributes.nsites or 0,
                        "nstructure_features": len(
                            resource.attributes.structure_features
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
                                "nelements": resource.attributes.nelements or 0,
                                "dimensionality": 3,
                                "nsites": resource.attributes.nsites or 0,
                                "nspecies": (
                                    len(resource.attributes.species)
                                    if resource.attributes.species
                                    else 0
                                ),
                                "nstructure_features": len(
                                    resource.attributes.structure_features
                                ),
                            },
                            properties=new_structure_attributes,
                        ),
                        "type": resource.type,
                        "id": resource.id,
                    },
                )

            dlite_collection.add(label=resource.id, inst=new_structure)

        update_collection(collection=dlite_collection)

        return DLiteSessionUpdate(collection_id=config.collection_id)

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

    def _get_explicit_resource_type(self) -> OPTIMADEResource | None:
        """Get the explicit resource type from the configuration.

        Returns:
            The explicit resource type if set, otherwise `None`.

        """
        parser_type = self.parse_config.parserType
        resource_type = parser_type.split("/")[-1]
        return optimade_resources.get(resource_type)

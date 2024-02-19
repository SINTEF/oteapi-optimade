"""OTEAPI strategy for parsing OPTIMADE structure resources to DLite instances."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import dlite
from optimade.adapters import Structure
from optimade.models import (
    Response as OPTIMADEResponse,
)
from optimade.models import (
    StructureResponseMany,
    StructureResponseOne,
    Success,
)
from oteapi.models import SessionUpdate
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEDLiteParseConfig, OPTIMADEParseSession
from oteapi_optimade.strategies.parse import OPTIMADEParseStrategy

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


LOGGER = logging.getLogger("oteapi_optimade.dlite")


@dataclass
class OPTIMADEDLiteParseStrategy:
    """Parse strategy for JSON.

    **Implements strategies**:

    - `("mediaType", "application/vnd.optimade+dlite")`
    - `("mediaType", "application/vnd.OPTIMADE+dlite")`
    - `("mediaType", "application/vnd.OPTiMaDe+dlite")`
    - `("mediaType", "application/vnd.optimade+DLite")`
    - `("mediaType", "application/vnd.OPTIMADE+DLite")`
    - `("mediaType", "application/vnd.OPTiMaDe+DLite")`

    """

    parse_config: OPTIMADEDLiteParseConfig

    def initialize(self, session: dict[str, Any] | None = None) -> DLiteSessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        return DLiteSessionUpdate(collection_id=get_collection(session).uuid)

    def get(
        self, session: SessionUpdate | dict[str, Any] | None = None
    ) -> OPTIMADEParseSession:
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

        Parameters:
            session: A session-specific dictionary-like context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        generic_parse_config = self.parse_config.model_copy(
            update={
                "mediaType": self.parse_config.mediaType.lower().replace(
                    "+dlite", "+json"
                )
            }
        ).model_dump()
        session = OPTIMADEParseStrategy(generic_parse_config).get(session)

        entities_path = Path(__file__).resolve().parent.resolve() / "entities"

        dlite.storage_path.append(str(entities_path / "*.yaml"))

        # JSONAPIResourceLinks = dlite.Instance.from_url(
        #     f"yaml://{entities_path}/JSONAPIResourceLinks.yaml"
        # )
        OPTIMADEStructure = dlite.Instance.from_url(
            f"yaml://{entities_path}/OPTIMADEStructure.yaml"
        )
        OPTIMADEStructureAssembly = dlite.Instance.from_url(
            f"yaml://{entities_path}/OPTIMADEStructureAssembly.yaml"
        )
        OPTIMADEStructureAttributes = dlite.Instance.from_url(
            f"yaml://{entities_path}/OPTIMADEStructureAttributes.yaml"
        )
        OPTIMADEStructureSpecies = dlite.Instance.from_url(
            f"yaml://{entities_path}/OPTIMADEStructureSpecies.yaml"
        )

        if not all(
            _ in session for _ in ("optimade_response", "optimade_response_model")
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
                session.get("optimade_response"),
                session.get("optimade_response_model"),
                list(session.keys()),
            )
            raise OPTIMADEParseError(base_error_message)

        optimade_response_model_module, optimade_response_model_name = session.get(
            "optimade_response_model"
        )
        optimade_response_dict = session.get("optimade_response")

        error_message_supporting_only_structures = (
            "The DLite OPTIMADE Parser currently only supports structures entities."
        )

        # Parse response using the provided model
        try:
            optimade_response_model: type[OPTIMADEResponse] = getattr(
                importlib.import_module(optimade_response_model_module),
                optimade_response_model_name,
            )
            optimade_response = optimade_response_model(**optimade_response_dict)
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
            structures = [
                (
                    Structure(entry)
                    if isinstance(entry, dict)
                    else Structure(entry.model_dump())
                )
                for entry in optimade_response.data
            ]
        elif isinstance(optimade_response, StructureResponseOne):
            structures = [
                (
                    Structure(optimade_response.data)
                    if isinstance(optimade_response.data, dict)
                    else Structure(optimade_response.data.model_dump())
                )
            ]
        elif isinstance(optimade_response, Success):
            if isinstance(optimade_response.data, dict):
                structures = [Structure(optimade_response.data)]
            elif isinstance(optimade_response.data, BaseModel):
                structures = [Structure(optimade_response.data.model_dump())]
            elif isinstance(optimade_response.data, list):
                structures = [
                    (
                        Structure(entry)
                        if isinstance(entry, dict)
                        else Structure(entry.model_dump())
                    )
                    for entry in optimade_response.data
                ]
            else:
                LOGGER.error(
                    "Could not determine what to do with `data`. Type %s.",
                    type(optimade_response.data),
                )
                error_message = "Could not parse `data` entry in response."
                raise OPTIMADEParseError(error_message)
        else:
            LOGGER.error(
                "Got currently unsupported response type %s. Only structures are "
                "supported.",
                optimade_response_model_name,
            )
            raise OPTIMADEParseError(error_message_supporting_only_structures)

        # DLite-fy OPTIMADE structures
        dlite_collection = get_collection(session)

        for structure in structures:
            new_structure_attributes: dict[str, Any] = {}

            # Most inner layer: assemblies & species
            if structure.attributes.assemblies:
                # Non-zero length list of assemblies (which could be a list of dicts or
                # a list of pydantic models)

                new_structure_attributes["assemblies"] = []

                for assembly in structure.attributes.assemblies:
                    # Ensure we're dealing with a normal Python dict
                    assembly_dict = (
                        assembly.model_dump(exclude_none=True)
                        if isinstance(assembly, BaseModel)
                        else assembly
                    )

                    dimensions = {
                        "ngroups": len(
                            assembly_dict.get("group_probabilities", []) or []
                        ),
                        "nsites": len(assembly_dict.get("sites_in_groups", []) or []),
                    }
                    new_structure_attributes["assemblies"].append(
                        OPTIMADEStructureAssembly(
                            dimensions=dimensions, properties=assembly_dict
                        )
                    )

            if structure.attributes.species:
                # Non-zero length list of species (which could be a list of dicts or a
                # list of pydantic models)

                new_structure_attributes["species"] = []

                for species_individual in structure.attributes.species:
                    # Ensure we're dealing with a normal Python dict
                    species_individual_dict = (
                        species_individual.model_dump(exclude_none=True)
                        if isinstance(species_individual, BaseModel)
                        else species_individual
                    )

                    dimensions = {
                        "nelements": len(
                            species_individual_dict.get("chemical_symbols", []) or []
                        ),
                        "nattached_elements": len(
                            species_individual_dict.get("attached", []) or []
                        ),
                    }
                    new_structure_attributes["species"].append(
                        OPTIMADEStructureSpecies(
                            dimensions=dimensions,
                            properties=species_individual_dict,
                        )
                    )

            # Attributes
            new_structure_attributes.update(
                structure.attributes.model_dump(
                    exclude={"species", "assemblies", "nelements", "nsites"}
                )
            )
            for key in list(new_structure_attributes):
                if key.startswith("_"):
                    new_structure_attributes.pop(key)

            # Structure features values are Enum values, so we need to convert them to
            # their string (true) values
            new_structure_attributes["structure_features"] = [
                _.value for _ in new_structure_attributes["structure_features"]
            ]

            new_structure = OPTIMADEStructure(
                dimensions={},
                properties={
                    "attributes": OPTIMADEStructureAttributes(
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
                    "type": structure.entry.type,
                    "id": structure.entry.id,
                },
            )
            dlite_collection.add(label=structure.entry.id, inst=new_structure)

        update_collection(collection=dlite_collection)

        return session

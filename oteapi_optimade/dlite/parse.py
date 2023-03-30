"""OTEAPI strategy for parsing OPTIMADE structure resources to DLite instances."""
# pylint: disable=invalid-name,too-many-branches,too-many-statements
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import dlite
from optimade.adapters import Structure
from optimade.models import StructureResponseMany, StructureResponseOne, Success
from oteapi.models import SessionUpdate
from oteapi_dlite.models import DLiteSessionUpdate
from oteapi_dlite.utils import get_collection, update_collection
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEDLiteParseConfig, OPTIMADEParseSession
from oteapi_optimade.strategies.parse import OPTIMADEParseStrategy

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Optional, Union


LOGGER = logging.getLogger("oteapi_optimade.dlite")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


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

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> DLiteSessionUpdate:
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
        self, session: "Optional[Union[SessionUpdate, Dict[str, Any]]]" = None
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
        session = OPTIMADEParseStrategy(self.parse_config).get(session)

        entities_path = Path(__file__).resolve().parent.resolve() / "entities"

        dlite.storage_path.append(str(entities_path / "*.json"))

        # JSONAPIResourceLinks = dlite.Instance.from_url(
        #     f"json://{entities_path}/JSONAPIResourceLinks.json"
        # )
        OPTIMADEStructure = dlite.Instance.from_url(
            f"json://{entities_path}/OPTIMADEStructure.json"
        )
        OPTIMADEStructureAssembly = dlite.Instance.from_url(
            f"json://{entities_path}/OPTIMADEStructureAssembly.json"
        )
        OPTIMADEStructureAttributes = dlite.Instance.from_url(
            f"json://{entities_path}/OPTIMADEStructureAttributes.json"
        )
        OPTIMADEStructureSpecies = dlite.Instance.from_url(
            f"json://{entities_path}/OPTIMADEStructureSpecies.json"
        )

        if self.parse_config.configuration.return_object:
            # The response is given as a "proper" pydantic data model instance

            if "optimade_response_object" not in session:
                raise ValueError(
                    "'optimade_response_object' was expected to be present in the "
                    "session."
                )

            # Currently, only "structures" entries are supported and handled
            if isinstance(session.optimade_response_object, StructureResponseMany):
                structures = [
                    Structure(entry)
                    if isinstance(entry, dict)
                    else Structure(entry.dict())
                    for entry in session.optimade_response_object.data
                ]
            elif isinstance(session.optimade_response_object, StructureResponseOne):
                structures = [
                    Structure(session.optimade_response_object.data)
                    if isinstance(session.optimade_response_object.data, dict)
                    else Structure(session.optimade_response_object.data.dict())
                ]
            elif isinstance(session.optimade_response_object, Success):
                if isinstance(session.optimade_response_object.data, dict):
                    structures = [Structure(session.optimade_response_object.data)]
                elif isinstance(session.optimade_response_object.data, BaseModel):
                    structures = [
                        Structure(session.optimade_response_object.data.dict())
                    ]
                elif isinstance(session.optimade_response_object.data, list):
                    structures = [
                        Structure(entry)
                        if isinstance(entry, dict)
                        else Structure(entry.dict())
                        for entry in session.optimade_response_object.data
                    ]
                else:
                    LOGGER.debug(
                        "Could not determine what to do with `data`. Type %s.",
                        type(session.optimade_response_object.data),
                    )
                    raise OPTIMADEParseError(
                        "Could not parse `data` entry in response."
                    )
            else:
                LOGGER.debug(
                    "Got currently unsupported response type %s. Only structures are "
                    "supported.",
                    session.optimade_response_object.__class__.__name__,
                )
                raise OPTIMADEParseError(
                    "The DLite OPTIMADE Parser currently only supports structures "
                    "entities."
                )
        else:
            # The response is given as pure Python dictionary

            if "optimade_response" not in session:
                raise ValueError(
                    "'optimade_response' was expected to be present in the session."
                )

            if not session.optimade_response or not "data" in session.optimade_response:
                LOGGER.debug("Not a successful response - no 'data' entry found.")
                return session

            if isinstance(session.optimade_response["data"], list):
                try:
                    structures = [
                        Structure(entry) for entry in session.optimade_response["data"]
                    ]
                except ValidationError as exc:
                    LOGGER.debug(
                        "Could not parse list of 'data' entries as structures."
                    )
                    raise OPTIMADEParseError(
                        "The DLite OPTIMADE Parser currently only supports structures "
                        "entities."
                    ) from exc
            elif session.optimade_response is not None:
                try:
                    structures = [Structure(session.optimade_response["data"])]
                except ValidationError as exc:
                    LOGGER.debug("Could not parse single 'data' entry as a structure.")
                    raise OPTIMADEParseError(
                        "The DLite OPTIMADE Parser currently only supports structures "
                        "entities."
                    ) from exc
            else:
                LOGGER.debug("Could not parse 'data' entries as structures.")
                raise OPTIMADEParseError(
                    "The DLite OPTIMADE Parser currently only supports structures "
                    "entities."
                )

        dlite_collection = get_collection(session)

        # DLite-fy OPTIMADE structures
        for structure in structures:
            new_structure_attributes = {}

            # Most inner layer: assemblies & species
            if structure.attributes.assemblies:
                dimensions = {
                    "ngroups": len(structure.attributes.assemblies),
                    "nsites": max(len(_) for _ in structure.attributes.assemblies),
                }
                new_structure_attributes["assemblies"] = OPTIMADEStructureAssembly(
                    dimensions=dimensions, properties=structure.attributes.assemblies
                )
            if structure.attributes.species:
                dimensions = {
                    "nelements": structure.attributes.nelements,
                    "nattached_elements": max(
                        _.nattached or 0 for _ in structure.attributes.species
                    ),
                }
                new_structure_attributes["species"] = [
                    OPTIMADEStructureSpecies(
                        dimensions=dimensions,
                        properties=species,
                    )
                    for species in structure.attributes.species
                ]

            # Attributes
            new_structure_attributes.update(
                structure.attributes.dict(exclude={"species", "assemblies"})
            )
            for key in list(new_structure_attributes):
                if key.startswith("_"):
                    new_structure_attributes.pop(key)

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
                            "nspecies": len(structure.attributes.species)
                            if structure.attributes.species
                            else 0,
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

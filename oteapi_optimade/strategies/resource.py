"""OPTIMADE resource strategy."""
import logging
import sys
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

import requests
from optimade.adapters import Reference, Structure
from optimade.models import (
    ErrorResponse,
    OptimadeError,
    ReferenceResponseMany,
    ReferenceResponseOne,
    StructureResponseMany,
    StructureResponseOne,
)
from oteapi.datacache import DataCache
from oteapi.models import SessionUpdate
from oteapi.plugins import create_strategy
from oteapi.plugins.entry_points import StrategyType
from pydantic.dataclasses import dataclass

try:
    from oteapi_dlite import __version__ as oteapi_dlite_version
    from oteapi_dlite.models import DLiteSessionUpdate
    from oteapi_dlite.utils import get_collection
except ImportError:
    oteapi_dlite_version = None

from oteapi_optimade.exceptions import MissingDependency, OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEResourceConfig, OPTIMADEResourceSession
from oteapi_optimade.models.custom_types import OPTIMADEUrl
from oteapi_optimade.models.query import OPTIMADEQueryParameters
from oteapi_optimade.utils import model2dict

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Optional, Union

    from optimade.models import Response as OPTIMADEResponse


LOGGER = logging.getLogger("oteapi_optimade.strategies")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


def use_dlite(access_service: str, use_dlite_flag: bool) -> bool:
    """Determine whether DLite should be utilized in the Resource strategy.

    Parameters:
        access_service: The accessService value from the resource's configuration.
        use_dlite_flag: The strategy-specific `use_dlite` configuration option.

    Returns:
        Based on the accessService value, then whether DLite should be used or not.

    """
    if (
        any(dlite_form in access_service for dlite_form in ["DLite", "dlite"])
        or use_dlite_flag
    ):
        if oteapi_dlite_version is None:
            raise MissingDependency(
                "OTEAPI-DLite is not found on the system. This is required to use "
                "DLite with the OTEAPI-OPTIMADE strategies."
            )
        return True
    return False


@dataclass
class OPTIMADEResourceStrategy:
    """OPTIMADE Resource Strategy.

    **Implements strategies**:

    - `("accessService", "optimade")`
    - `("accessService", "OPTIMADE")`
    - `("accessService", "OPTiMaDe")`
    - `("accessService", "optimade+dlite")`
    - `("accessService", "OPTIMADE+dlite")`
    - `("accessService", "OPTiMaDe+dlite")`
    - `("accessService", "optimade+DLite")`
    - `("accessService", "OPTIMADE+DLite")`
    - `("accessService", "OPTiMaDe+DLite")`

    """

    resource_config: OPTIMADEResourceConfig

    def initialize(  # pylint: disable=unused-argument
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Union[SessionUpdate, DLiteSessionUpdate]":
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if use_dlite(
            self.resource_config.accessService,
            self.resource_config.configuration.use_dlite,
        ):
            return DLiteSessionUpdate(collection_id=get_collection(session).uuid)
        return SessionUpdate()

    def get(  # pylint: disable=too-many-branches,too-many-statements
        self, session: "Optional[Union[SessionUpdate, Dict[str, Any]]]" = None
    ) -> OPTIMADEResourceSession:
        """Execute an OPTIMADE query to `accessUrl`.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Configuration values provided in `resource_config.configuration` take
        precedence over the derived values from `accessUrl`.

        Workflow:
        1. Update configuration according to session.
        2. Deconstruct `accessUrl` (done partly by
           `oteapi_optimade.models.custom_types.OPTIMADEUrl`).
        3. Reconstruct the complete query URL.
        4. Send query.
        5. Store result in data cache.

        Parameters:
            session: A session-specific dictionary-like context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if session and isinstance(session, dict):
            session = OPTIMADEResourceSession(**session)
        elif session and isinstance(session, SessionUpdate):
            session = OPTIMADEResourceSession(
                **model2dict(session, exclude_defaults=True, exclude_unset=True)
            )
        else:
            session = OPTIMADEResourceSession()

        if session.optimade_config:
            self.resource_config.configuration.update(
                model2dict(
                    session.optimade_config, exclude_defaults=True, exclude_unset=True
                )
            )

        optimade_endpoint = self.resource_config.accessUrl.endpoint or "structures"
        optimade_query = (
            self.resource_config.configuration.query_parameters
            or OPTIMADEQueryParameters()
        )
        LOGGER.debug("resource_config: %r", self.resource_config)

        if self.resource_config.accessUrl.query:
            parsed_query = parse_qs(self.resource_config.accessUrl.query)
            for field, value in parsed_query.items():
                # Only use the latest defined value for any parameter
                if field not in optimade_query.__fields_set__:
                    LOGGER.debug(
                        "Setting %r from accessUrl (value=%r)", field, value[-1]
                    )
                    setattr(optimade_query, field, value[-1])

        LOGGER.debug("optimade_query after update: %r", optimade_query)

        optimade_url = OPTIMADEUrl(
            f"{self.resource_config.accessUrl.base_url}"
            f"/{self.resource_config.accessUrl.version or 'v1'}"
            f"/{optimade_endpoint}?{optimade_query.generate_query_string()}"
        )
        LOGGER.debug("OPTIMADE URL to be requested: %s", optimade_url)

        # Set cache access key to the full OPTIMADE URL.
        self.resource_config.configuration.datacache_config.accessKey = optimade_url

        # Perform query
        response = requests.get(
            optimade_url,
            allow_redirects=True,
            timeout=(3, 27),  # timeout in seconds (connect, read)
        )

        if optimade_query.response_format and optimade_query.response_format != "json":
            raise NotImplementedError(
                "Can only handle JSON responses for now. Requested response format: "
                f"{optimade_query.response_format!r}"
            )

        cache = DataCache(config=self.resource_config.configuration.datacache_config)
        cache.add(
            {
                "status_code": response.status_code,
                "ok": response.ok,
                "json": response.json(),
            }
        )

        parse_with_dlite = use_dlite(
            self.resource_config.accessService,
            self.resource_config.configuration.use_dlite,
        )

        parse_mediaType = f"application/vnd.{self.resource_config.accessService.split('+', maxsplit=1)[0]}"  # pylint: disable=invalid-name,line-too-long
        if parse_with_dlite:
            parse_mediaType += "+DLite"  # pylint: disable=invalid-name
        elif optimade_query.response_format:
            parse_mediaType += (  # pylint: disable=invalid-name
                f"+{optimade_query.response_format}"
            )

        parse_config = {
            "downloadUrl": optimade_url,
            "mediaType": parse_mediaType,
            "configuration": {
                "datacache_config": self.resource_config.configuration.datacache_config,
                "return_object": True,
            },
        }

        session.update(
            create_strategy(StrategyType.PARSE, parse_config).initialize(
                model2dict(session, exclude_defaults=True, exclude_unset=True)
            )
        )
        session.update(
            create_strategy(StrategyType.PARSE, parse_config).get(
                model2dict(session, exclude_defaults=True, exclude_unset=True)
            )
        )

        if "optimade_response_object" not in session:
            raise ValueError(
                "'optimade_response_object' was expected to be present in the session."
            )
        optimade_response: "OPTIMADEResponse" = session.pop("optimade_response_object")
        if "optimade_response" in session and not session.get("optimade_response"):
            del session["optimade_response"]

        if isinstance(optimade_response, ErrorResponse):
            optimade_resources = optimade_response.errors
            session.optimade_resource_model = (
                f"{OptimadeError.__module__}:OptimadeError"
            )
        elif isinstance(optimade_response, ReferenceResponseMany):
            optimade_resources = [
                Reference(entry).as_dict
                if isinstance(entry, dict)
                else Reference(entry.dict()).as_dict
                for entry in optimade_response.data
            ]
            session.optimade_resource_model = f"{Reference.__module__}:Reference"
        elif isinstance(optimade_response, ReferenceResponseOne):
            optimade_resources = [
                Reference(optimade_response.data).as_dict
                if isinstance(optimade_response.data, dict)
                else Reference(optimade_response.data.dict()).as_dict
            ]
            session.optimade_resource_model = f"{Reference.__module__}:Reference"
        elif isinstance(optimade_response, StructureResponseMany):
            optimade_resources = [
                Structure(entry).as_dict
                if isinstance(entry, dict)
                else Structure(entry.dict()).as_dict
                for entry in optimade_response.data
            ]
            session.optimade_resource_model = f"{Structure.__module__}:Structure"
        elif isinstance(optimade_response, StructureResponseOne):
            optimade_resources = [
                Structure(optimade_response.data).as_dict
                if isinstance(optimade_response.data, dict)
                else Structure(optimade_response.data.dict()).as_dict
            ]
            session.optimade_resource_model = f"{Structure.__module__}:Structure"
        else:
            LOGGER.debug(
                "Could not parse response as errors, references or structures. "
                "Response:\n%r",
                optimade_response,
            )
            raise OPTIMADEParseError(
                "Could not retrieve errors, references or structures from response "
                f"from {optimade_url}. It could be a valid OPTIMADE API response, "
                "however it may not be supported by OTEAPI-OPTIMADE. It may also be an "
                "invalid response completely."
            )

        session.optimade_resources = [
            model2dict(resource) for resource in optimade_resources
        ]

        if session.optimade_config and session.optimade_config.query_parameters:
            session = session.copy(
                update={
                    "optimade_config": session.optimade_config.copy(
                        update={
                            "query_parameters": model2dict(
                                session.optimade_config.query_parameters,
                                exclude_defaults=True,
                                exclude_unset=True,
                            )
                        }
                    )
                }
            )

        return session

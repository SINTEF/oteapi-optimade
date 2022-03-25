"""OPTIMADE resource strategy."""
import logging
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

import requests
from optimade.adapters import Reference, Structure
from optimade.models import (
    ErrorResponse,
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

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEResourceConfig, OPTIMADEResourceSession
from oteapi_optimade.models.custom_types import OPTIMADEUrl
from oteapi_optimade.models.query import OPTIMADEQueryParameters

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union


LOGGER = logging.getLogger("oteapi_optimade.strategies")
LOGGER.setLevel(logging.DEBUG)


@dataclass
class OPTIMADEResourceStrategy:
    """OPTIMADE Resource Strategy.

    **Implements strategies**:

    - `("accessService", "optimade")`
    - `("accessService", "OPTIMADE")`
    - `("accessService", "OPTiMaDe")`

    """

    resource_config: OPTIMADEResourceConfig

    def initialize(  # pylint: disable=no-self-use,unused-argument
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> SessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        return SessionUpdate()

    def get(  # pylint: disable=too-many-branches
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
        session = (
            OPTIMADEResourceSession(**session) if session else OPTIMADEResourceSession()
        )
        self._use_session(session)

        optimade_base_url = (
            self.resource_config.configuration.base_url
            or self.resource_config.accessUrl.base_url
        )
        optimade_path = ""
        optimade_query = (
            self.resource_config.configuration.query_parameters
            or OPTIMADEQueryParameters()
        )
        LOGGER.debug("resource_config: %r", self.resource_config)

        if self.resource_config.configuration.base_url:
            if (
                self.resource_config.accessUrl.base_url
                != self.resource_config.configuration.base_url
            ):
                optimade_path = str(self.resource_config.accessUrl)[
                    len(self.resource_config.configuration.base_url) :
                ]
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
            f"{optimade_base_url}{optimade_path}?{optimade_query.generate_query_string()}"
        )

        # Set cache access key to the full OPTIMADE URL.
        self.resource_config.configuration.datacache_config.accessKey = optimade_url

        # Perform query
        response = requests.get(optimade_url, allow_redirects=True)

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

        parse_config = {
            "downloadUrl": optimade_url,
            "mediaType": f"application/vnd.optimade+{optimade_query.response_format}",
            "configuration": {
                "datacache_config": self.resource_config.configuration.datacache_config,
                "return_object": True,
            },
        }

        session.update(
            create_strategy(StrategyType.PARSE, parse_config).initialize(session)
        )
        session.update(create_strategy(StrategyType.PARSE, parse_config).get(session))

        if "optimade_response_object" not in session:
            raise ValueError(
                "'optimade_response_object' was expected to be present in the session."
            )
        optimade_response = session.pop("optimade_response_object")

        if isinstance(optimade_response, ErrorResponse):
            session.optimade_errors = optimade_response.errors
        elif isinstance(optimade_response, ReferenceResponseMany):
            session.optimade_references = [
                Reference(entry) if isinstance(entry, dict) else Reference(entry.dict())
                for entry in optimade_response.data
            ]
        elif isinstance(optimade_response, ReferenceResponseOne):
            session.optimade_references = [
                Reference(optimade_response.data)
                if isinstance(optimade_response.data, dict)
                else Reference(optimade_response.data.dict())
            ]
        elif isinstance(optimade_response, StructureResponseMany):
            session.optimade_structures = [
                Structure(entry) if isinstance(entry, dict) else Structure(entry.dict())
                for entry in optimade_response.data
            ]
        elif isinstance(optimade_response, StructureResponseOne):
            session.optimade_structures = [
                Structure(optimade_response.data)
                if isinstance(optimade_response.data, dict)
                else Structure(optimade_response.data.dict())
            ]
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

        return session

    def _use_session(self, session: OPTIMADEResourceSession) -> None:
        """Update OPTIMADE-specific configuration according to values found in the
        session."""
        if session.optimade_config:
            self.resource_config.configuration = session.optimade_config

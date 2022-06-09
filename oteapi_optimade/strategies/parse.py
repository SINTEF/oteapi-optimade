"""Demo strategy class for text/json."""
import json
import logging
import sys
from typing import TYPE_CHECKING

from optimade.models import ErrorResponse, Success
from oteapi.datacache import DataCache
from oteapi.models import SessionUpdate
from oteapi.plugins import create_strategy
from oteapi.plugins.entry_points import StrategyType
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEParseConfig, OPTIMADEParseSession
from oteapi_optimade.utils import model2dict

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union


LOGGER = logging.getLogger("oteapi_optimade.strategies")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


@dataclass
class OPTIMADEParseStrategy:
    """Parse strategy for JSON.

    **Implements strategies**:

    - `("mediaType", "application/vnd.optimade+json")`
    - `("mediaType", "application/vnd.OPTIMADE+json")`
    - `("mediaType", "application/vnd.OPTiMaDe+json")`
    - `("mediaType", "application/vnd.optimade+JSON")`
    - `("mediaType", "application/vnd.OPTIMADE+JSON")`
    - `("mediaType", "application/vnd.OPTiMaDe+JSON")`
    - `("mediaType", "application/vnd.optimade")`
    - `("mediaType", "application/vnd.OPTIMADE")`
    - `("mediaType", "application/vnd.OPTiMaDe")`

    """

    parse_config: OPTIMADEParseConfig

    def initialize(  # pylint: disable=unused-argument
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
    ) -> OPTIMADEParseSession:
        """Request and parse an OPTIMADE response using OPT.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Configuration values provided in `resource_config.configuration` take
        precedence over the derived values from `downloadUrl`.

        Workflow:
        1. Request OPTIMADE response.
        2. Parse as an OPTIMADE Python tools (OPT) pydantic response model.

        Parameters:
            session: A session-specific dictionary-like context.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if session and isinstance(session, dict):
            session = OPTIMADEParseSession(**session)
        elif session and isinstance(session, SessionUpdate):
            session = OPTIMADEParseSession(
                **model2dict(session, exclude_defaults=True, exclude_unset=True)
            )
        else:
            session = OPTIMADEParseSession()

        if session.optimade_config:
            self.parse_config.configuration.update(
                model2dict(
                    session.optimade_config, exclude_defaults=True, exclude_unset=True
                )
            )

        cache = DataCache(self.parse_config.configuration.datacache_config)
        if self.parse_config.downloadUrl in cache:
            response: "Dict[str, Any]" = cache.get(self.parse_config.downloadUrl)
        elif (
            self.parse_config.configuration.datacache_config.accessKey
            and self.parse_config.configuration.datacache_config.accessKey in cache
        ):
            response = cache.get(
                self.parse_config.configuration.datacache_config.accessKey
            )
        else:
            download_config = self.parse_config.copy()
            session.update(
                create_strategy(StrategyType.DOWNLOAD, download_config).initialize(
                    model2dict(session, exclude_defaults=True, exclude_unset=True)
                )
            )
            session.update(
                create_strategy(StrategyType.DOWNLOAD, download_config).get(
                    model2dict(session, exclude_defaults=True, exclude_unset=True)
                )
            )

            response = {"json": json.loads(cache.get(session.pop("key")))}

        if (
            not response.get("ok", True)
            or (
                200 > response.get("status_code", 200)
                or response.get("status_code", 200) >= 300
            )
            or "errors" in response.get("json", {})
        ):
            # Error response
            try:
                response_object = ErrorResponse(**response.get("json", {}))
            except ValidationError as exc:
                LOGGER.error(
                    "Could not validate an error response.\nValidationError: "
                    "%s\nresponse=%r",
                    exc,
                    response,
                )
                raise OPTIMADEParseError(
                    "Could not validate an error response."
                ) from exc
        else:
            # Successful response
            response_model = self.parse_config.downloadUrl.response_model()
            if response_model:
                if not isinstance(response_model, tuple):
                    response_model = (response_model,)
                for model_cls in response_model:
                    try:
                        response_object = model_cls(**response.get("json", {}))
                    except ValidationError:
                        pass
                    else:
                        break
                else:
                    LOGGER.error(
                        "Could not validate for an expected response model.\nURL=%r\n"
                        "response_models=%r\nresponse=%s",
                        self.parse_config.downloadUrl,
                        response_model,
                        response,
                    )
                    raise OPTIMADEParseError(
                        "Could not validate for an expected response model."
                    )
            else:
                # No "endpoint" or unknown
                try:
                    response_object = Success(**response.get("json", {}))
                except ValidationError as exc:
                    LOGGER.error(
                        "Unknown or unparseable endpoint.\nValidatonError: %s\n"
                        "URL=%r\nendpoint=%r\nresponse_model=%r\nresponse=%s",
                        exc,
                        self.parse_config.downloadUrl,
                        self.parse_config.downloadUrl.endpoint,
                        response_model,
                        response,
                    )
                    raise OPTIMADEParseError(
                        "Unknown or unparseable endpoint."
                    ) from exc

        if self.parse_config.configuration.return_object:
            session.optimade_response_object = response_object
        else:
            session.optimade_response = model2dict(response_object)

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

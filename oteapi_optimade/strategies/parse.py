"""Demo strategy class for text/json."""

from __future__ import annotations

import json
import logging
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

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


LOGGER = logging.getLogger("oteapi_optimade.strategies")


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

    def initialize(
        self,
        session: dict[str, Any] | None = None,  # noqa: ARG002
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
                **session.model_dump(exclude_defaults=True, exclude_unset=True)
            )
        else:
            session = OPTIMADEParseSession()

        if session.optimade_config:
            self.parse_config.configuration.update(
                session.optimade_config.model_dump(
                    exclude_defaults=True, exclude_unset=True
                )
            )

        cache = DataCache(self.parse_config.configuration.datacache_config)
        if self.parse_config.downloadUrl in cache:
            response: dict[str, Any] = cache.get(self.parse_config.downloadUrl)
        elif (
            self.parse_config.configuration.datacache_config.accessKey
            and self.parse_config.configuration.datacache_config.accessKey in cache
        ):
            response = cache.get(
                self.parse_config.configuration.datacache_config.accessKey
            )
        else:
            download_config = self.parse_config.model_copy()
            session.update(
                create_strategy(StrategyType.DOWNLOAD, download_config).initialize(
                    session.model_dump(exclude_defaults=True, exclude_unset=True)
                )
            )
            session.update(
                create_strategy(StrategyType.DOWNLOAD, download_config).get(
                    session.model_dump(exclude_defaults=True, exclude_unset=True)
                )
            )

            response = {"json": json.loads(cache.get(session.pop("key")))}

        if (
            not response.get("ok", True)
            or (
                response.get("status_code", 200) < 200
                or response.get("status_code", 200) >= 300
            )
            or "errors" in response.get("json", {})
        ):
            # Error response
            try:
                response_object = ErrorResponse(**response.get("json", {}))
            except ValidationError as exc:
                error_message = "Could not validate an error response."
                LOGGER.error(
                    "%s\nValidationError: " "%s\nresponse=%r",
                    error_message,
                    exc,
                    response,
                )
                raise OPTIMADEParseError(error_message) from exc
        else:
            # Successful response
            response_model = self.parse_config.downloadUrl.response_model()
            LOGGER.debug("response_model=%r", response_model)
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
                    error_message = "Could not validate for an expected response model."
                    LOGGER.error(
                        "%s\nURL=%r\n" "response_models=%r\nresponse=%s",
                        error_message,
                        self.parse_config.downloadUrl,
                        response_model,
                        response,
                    )
                    raise OPTIMADEParseError(error_message)
            else:
                # No "endpoint" or unknown
                LOGGER.debug("No response_model, using Success response model.")
                try:
                    response_object = Success(**response.get("json", {}))
                except ValidationError as exc:
                    error_message = "Unknown or unparseable endpoint."
                    LOGGER.error(
                        "%s\nValidatonError: %s\n"
                        "URL=%r\nendpoint=%r\nresponse_model=%r\nresponse=%s",
                        error_message,
                        exc,
                        self.parse_config.downloadUrl,
                        self.parse_config.downloadUrl.endpoint,
                        response_model,
                        response,
                    )
                    raise OPTIMADEParseError(error_message) from exc

        session.optimade_response_model = (
            response_object.__class__.__module__,
            response_object.__class__.__name__,
        )
        session.optimade_response = response_object.model_dump(exclude_unset=True)

        if session.optimade_config and session.optimade_config.query_parameters:
            session = session.model_copy(
                update={
                    "optimade_config": session.optimade_config.model_copy(
                        update={
                            "query_parameters": session.optimade_config.query_parameters.model_dump(
                                exclude_defaults=True,
                                exclude_unset=True,
                            )
                        }
                    )
                }
            )

        if TYPE_CHECKING:  # pragma: no cover
            assert isinstance(session, OPTIMADEParseSession)  # nosec

        return session

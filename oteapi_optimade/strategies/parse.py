"""Demo strategy class for text/json."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from optimade.models import ErrorResponse, Success
from oteapi.datacache import DataCache
from oteapi.models import AttrDict
from oteapi.plugins import create_strategy
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from oteapi_optimade.exceptions import OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEParseConfig, OPTIMADEParseResult

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


LOGGER = logging.getLogger(__name__)


@dataclass
class OPTIMADEParseStrategy:
    """Parse strategy for JSON.

    **Implements strategies**:

    - `("parserType", "parser/OPTIMADE")`

    """

    parse_config: OPTIMADEParseConfig

    def initialize(self) -> AttrDict:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        return AttrDict()

    def get(self) -> OPTIMADEParseResult:
        """Request and parse an OPTIMADE response using OPT.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Configuration values provided in `resource_config.configuration` take
        precedence over the derived values from `downloadUrl`.

        Workflow:

        1. Request OPTIMADE response.
        2. Parse as an OPTIMADE Python tools (OPT) pydantic response model.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if (
            self.parse_config.configuration.downloadUrl is None
            or self.parse_config.configuration.mediaType is None
        ):
            raise OPTIMADEParseError(
                "Missing downloadUrl or mediaType in configuration."
            )

        cache = DataCache(self.parse_config.configuration.datacache_config)
        if self.parse_config.configuration.downloadUrl in cache:
            response: dict[str, Any] = cache.get(
                self.parse_config.configuration.downloadUrl
            )
        elif (
            self.parse_config.configuration.datacache_config.accessKey
            and self.parse_config.configuration.datacache_config.accessKey in cache
        ):
            response = cache.get(
                self.parse_config.configuration.datacache_config.accessKey
            )
        else:
            download_config = self.parse_config.configuration.model_copy()
            download_output = create_strategy("download", download_config).get()
            response = {"json": json.loads(cache.get(download_output.pop("key")))}

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
            response_model = (
                self.parse_config.configuration.downloadUrl.response_model()
            )
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
                        self.parse_config.configuration.downloadUrl,
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
                        self.parse_config.configuration.downloadUrl,
                        self.parse_config.configuration.downloadUrl.endpoint,
                        response_model,
                        response,
                    )
                    raise OPTIMADEParseError(error_message) from exc

        result = OPTIMADEParseResult(
            model_config=self.parse_config.configuration.model_dump(),
            optimade_response_model=(
                response_object.__class__.__module__,
                response_object.__class__.__name__,
            ),
            optimade_response=response_object.model_dump(exclude_unset=True),
        )

        if (
            self.parse_config.configuration.optimade_config
            and self.parse_config.configuration.optimade_config.query_parameters
        ):
            result = result.model_copy(
                update={
                    "optimade_config": self.parse_config.configuration.optimade_config.model_copy(
                        update={
                            "query_parameters": self.parse_config.configuration.optimade_config.query_parameters.model_dump(
                                exclude_defaults=True,
                                exclude_unset=True,
                            )
                        }
                    )
                }
            )

        return result

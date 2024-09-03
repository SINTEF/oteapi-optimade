"""OPTIMADE resource strategy."""

from __future__ import annotations

import importlib
import logging
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
from oteapi.models import AttrDict
from oteapi.plugins import create_strategy
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

try:
    from oteapi_dlite import __version__ as oteapi_dlite_version
    from oteapi_dlite.models import DLiteSessionUpdate
    from oteapi_dlite.utils import get_collection
except ImportError:
    oteapi_dlite_version = None

from oteapi_optimade.exceptions import MissingDependency, OPTIMADEParseError
from oteapi_optimade.models import OPTIMADEResourceConfig, OPTIMADEResourceResult
from oteapi_optimade.models.custom_types import OPTIMADEUrl
from oteapi_optimade.models.query import OPTIMADEQueryParameters

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, TypedDict

    from optimade.models import Response as OPTIMADEResponse

    class ParseConfigDict(TypedDict):
        """Type definition for the `parse_config` dictionary."""

        entity: str
        parserType: str
        configuration: dict[str, Any]


LOGGER = logging.getLogger(__name__)


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
            error_message = (
                "OTEAPI-DLite is not found on the system. This is required to use "
                "DLite with the OTEAPI-OPTIMADE strategies."
            )
            raise MissingDependency(error_message)
        return True
    return False


@dataclass
class OPTIMADEResourceStrategy:
    """OPTIMADE Resource Strategy.

    **Implements strategies**:

    - `("accessService", "OPTIMADE")`
    - `("accessService", "OPTIMADE+DLite")`

    """

    resource_config: OPTIMADEResourceConfig

    def initialize(self) -> AttrDict | DLiteSessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if use_dlite(
            self.resource_config.accessService,
            self.resource_config.configuration.use_dlite,
        ):
            collection_id = self.resource_config.configuration.get(
                "collection_id", None
            )
            return DLiteSessionUpdate(
                collection_id=get_collection(collection_id=collection_id).uuid
            )

        return AttrDict()

    def get(self) -> OPTIMADEResourceResult:
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

        Returns:
            An update model of key/value-pairs to be stored in the session-specific
            context from services.

        """
        if self.resource_config.configuration.optimade_config:
            self.resource_config.configuration.update(
                self.resource_config.configuration.optimade_config.model_dump(
                    exclude_defaults=True,
                    exclude_unset=True,
                    exclude={"optimade_config", "downloadUrl", "mediaType"},
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
                if field not in optimade_query.model_fields_set:
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
            error_message = (
                "Can only handle JSON responses for now. Requested response format: "
                f"{optimade_query.response_format!r}"
            )
            raise NotImplementedError(error_message)

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

        parse_parserType = "parser/OPTIMADE"
        parse_mediaType = (
            "application/vnd."
            f"{self.resource_config.accessService.split('+', maxsplit=1)[0]}"
        )
        if parse_with_dlite:
            parse_parserType += "/DLite"
            parse_mediaType += "+DLite"
        elif optimade_query.response_format:
            parse_mediaType += f"+{optimade_query.response_format}"

        parse_config: ParseConfigDict = {
            "entity": "http://onto-ns.com/meta/1.0.1/OPTIMADEStructure",
            "parserType": parse_parserType,
            "configuration": {
                "datacache_config": self.resource_config.configuration.datacache_config.model_copy(),
                "downloadUrl": str(optimade_url),
                "mediaType": parse_mediaType,
                "optimade_config": self.resource_config.configuration.model_dump(
                    exclude={"optimade_config", "downloadUrl", "mediaType"},
                    exclude_unset=True,
                    exclude_defaults=True,
                ),
            },
        }

        LOGGER.debug("parse_config: %r", parse_config)

        parse_config["configuration"].update(
            create_strategy("parse", parse_config).initialize()
        )
        parse_result = create_strategy("parse", parse_config).get()

        if not all(
            _ in parse_result for _ in ("optimade_response", "optimade_response_model")
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
                parse_result.get("optimade_response"),
                parse_result.get("optimade_response_model"),
                list(parse_result.keys()),
            )
            raise OPTIMADEParseError(base_error_message)

        optimade_response_model_module, optimade_response_model_name = parse_result.pop(
            "optimade_response_model"
        )
        optimade_response_dict = parse_result.pop("optimade_response")

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

        result = OPTIMADEResourceResult()

        if isinstance(optimade_response, ErrorResponse):
            optimade_resources = optimade_response.errors
            result.optimade_resource_model = f"{OptimadeError.__module__}:OptimadeError"
        elif isinstance(optimade_response, ReferenceResponseMany):
            optimade_resources = [
                (
                    Reference(entry).as_dict
                    if isinstance(entry, dict)
                    else Reference(entry.model_dump()).as_dict
                )
                for entry in optimade_response.data
            ]
            result.optimade_resource_model = f"{Reference.__module__}:Reference"
        elif isinstance(optimade_response, ReferenceResponseOne):
            optimade_resources = [
                (
                    Reference(optimade_response.data).as_dict
                    if isinstance(optimade_response.data, dict)
                    else Reference(optimade_response.data.model_dump()).as_dict
                )
            ]
            result.optimade_resource_model = f"{Reference.__module__}:Reference"
        elif isinstance(optimade_response, StructureResponseMany):
            optimade_resources = [
                (
                    Structure(entry).as_dict
                    if isinstance(entry, dict)
                    else Structure(entry.model_dump()).as_dict
                )
                for entry in optimade_response.data
            ]
            result.optimade_resource_model = f"{Structure.__module__}:Structure"
        elif isinstance(optimade_response, StructureResponseOne):
            optimade_resources = [
                (
                    Structure(optimade_response.data).as_dict
                    if isinstance(optimade_response.data, dict)
                    else Structure(optimade_response.data.model_dump()).as_dict
                )
            ]
            result.optimade_resource_model = f"{Structure.__module__}:Structure"
        else:
            LOGGER.error(
                "Could not parse response as errors, references or structures. "
                "Response:\n%r",
                optimade_response,
            )
            error_message = (
                "Could not retrieve errors, references or structures from response "
                f"from {optimade_url}. It could be a valid OPTIMADE API response, "
                "however it may not be supported by OTEAPI-OPTIMADE. It may also be an "
                "invalid response completely."
            )
            raise OPTIMADEParseError(error_message)

        result.optimade_resources = [
            resource if isinstance(resource, dict) else resource.model_dump()
            for resource in optimade_resources
        ]

        if (
            self.resource_config.configuration.optimade_config
            and self.resource_config.configuration.optimade_config.query_parameters
        ):
            result = result.model_copy(
                update={
                    "optimade_config": self.resource_config.configuration.optimade_config.model_copy(
                        update={
                            "query_parameters": self.resource_config.configuration.optimade_config.query_parameters.model_dump(
                                exclude_defaults=True,
                                exclude_unset=True,
                            )
                        }
                    )
                }
            )

        return result

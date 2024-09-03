"""Custom "pydantic" types used in OTEAPI-OPTIMADE."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, ClassVar, cast, no_type_check

from optimade.models import (
    EntryInfoResponse,
    EntryResponseMany,
    EntryResponseOne,
    InfoResponse,
    LinksResponse,
    ReferenceResponseMany,
    ReferenceResponseOne,
    StructureResponseMany,
    StructureResponseOne,
    Success,
)
from pydantic import AnyHttpUrl, ValidationError
from pydantic_core import Url, core_schema

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Optional, TypedDict, Union

    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema

    class OPTIMADEParts(TypedDict, total=False):
        """Similar to `pydantic.networks.Parts`."""

        base_url: str
        version: str | None
        endpoint: str | None
        query: str | None


_OPTIMADE_BASE_URL_REGEX = re.compile(
    r"^(?P<base_url>"
    # scheme https://tools.ietf.org/html/rfc3986#appendix-A
    r"(?:[a-z][a-z0-9+\-.]+://)?"
    r"(?:[^\s:/]*(?::[^\s/]*)?@)?"  # user info
    r"(?:"
    r"(?:\d{1,3}\.){3}\d{1,3}(?=$|[/:#?])|"  # ipv4
    r"\[[A-F0-9]*:[A-F0-9:]+\](?=$|[/:#?])|"  # ipv6
    r"[^\s/:?#]+"  # domain, validation occurs later
    r")?"
    r"(?::\d+)?"  # port
    r"(?P<path>/[^\s?#]*)?"  # path
    r")",
    re.IGNORECASE,
)
_OPTIMADE_ENDPOINT_REGEX = re.compile(
    # version
    r"(?:/(?P<version>v[0-9]+(?:\.[0-9+]){0,2})"
    r"(?=/info|/links|/version|/structures|/references|/calculations"
    r"|/extensions))?"
    # endpoint
    r"(?:/(?P<endpoint>(?:info|links|versions|structures|references"
    r"|calculations|extensions)(?:/[^\s?#]*)?))?$"
)

LOGGER = logging.getLogger(__name__)


class OPTIMADEUrl(str):
    """A deconstructed OPTIMADE URL.

    An OPTIMADE URL is made up in the following way:

        <BASE URL>[/<VERSION>]/<ENDPOINT>?[<QUERY PARAMETERS>]

    Where parts in square brackets (`[]`) are optional.
    """

    # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
    max_length = 2083
    allowed_schemes: ClassVar[list[str]] = ["http", "https"]
    host_required = True

    @no_type_check
    def __new__(cls, url: str | None = None, **kwargs) -> object:
        return str.__new__(
            cls,
            url if url else cls._build(**kwargs),
        )

    def __init__(
        self,
        url: str,
        *,
        base_url: Optional[str] = None,
        version: Optional[str] = None,
        endpoint: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        str.__init__(url)

        # Parse as URL
        try:
            pydantic_url = AnyHttpUrl(url)
        except ValidationError:
            try:
                pydantic_url = AnyHttpUrl(
                    self._build(
                        base_url=base_url or "",
                        version=version,
                        endpoint=endpoint,
                        query=query,
                    )
                )
            except ValidationError:
                pydantic_url = None

        # Build OPTIMADE URL parts
        optimade_parts: Union[OPTIMADEParts, dict[str, Any]] = {}
        if pydantic_url:
            optimade_parts = self._build_optimade_parts(pydantic_url)

        self._base_url = base_url or optimade_parts.get("base_url", None)
        self._version = version or optimade_parts.get("version", None)
        self._endpoint = endpoint or optimade_parts.get("endpoint", None)
        self._query = query or optimade_parts.get("query", None)
        self._scheme = self._base_url.split("://")[0] if self._base_url else None

    def __str__(self) -> str:
        return self._build(
            base_url=self.base_url,
            version=self.version,
            endpoint=self.endpoint,
            query=self.query,
        )

    def __repr__(self) -> str:
        extra = ", ".join(
            f"{n}={getattr(self, n)!r}"
            for n in ("scheme", "base_url", "version", "endpoint", "query")
            if getattr(self, n) is not None
        )
        return f"{self.__class__.__name__}({super().__repr__()}, {extra})"

    @staticmethod
    def _build(
        *,
        base_url: str,
        version: Optional[str] = None,
        endpoint: Optional[str] = None,
        query: Optional[str] = None,
    ) -> str:
        """Build complete OPTIMADE URL from URL parts."""
        url = base_url.rstrip("/")
        if version:
            url += f"/{version}"
        if endpoint:
            url += f"/{endpoint}"
        if query:
            url += f"?{query}"
        return url

    @property
    def scheme(self) -> str:
        """The scheme of the OPTIMADE URL."""
        if self._scheme is None:
            error_message = "OPTIMADE URL has no scheme."
            raise ValueError(error_message)
        return self._scheme

    @property
    def base_url(self) -> str:
        """The base URL of the OPTIMADE URL."""
        if self._base_url is None:
            error_message = "OPTIMADE URL has no base URL."
            raise ValueError(error_message)
        return self._base_url

    @property
    def version(self) -> Optional[str]:
        """The version part of the OPTIMADE URL."""
        return self._version

    @property
    def endpoint(self) -> Optional[str]:
        """The endpoint part of the OPTIMADE URL."""
        return self._endpoint

    @property
    def query(self) -> Optional[str]:
        """The query part of the OPTIMADE URL."""
        return self._query

    def response_model(self) -> Union[tuple[Success, Success], Success, None]:
        """Return the endpoint's corresponding response model(s) (from OPT)."""
        if not self.endpoint or self.endpoint == "versions":
            return None

        return {
            "info": (InfoResponse, EntryInfoResponse),
            "links": LinksResponse,
            "structures": (StructureResponseMany, StructureResponseOne),
            "references": (ReferenceResponseMany, ReferenceResponseOne),
            "calculations": (EntryResponseMany, EntryResponseOne),
        }.get(self.endpoint, Success)

    # Pydantic-related methods
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Pydantic core schema for an OPTIMADE URL.

        Behaviour:
        - strings and `Url` instances will be parsed as `pydantic.AnyHttpUrl` instances
          and then converted to `OPTIMADEUrl` instances.
        - `OPTIMADEUrl` instances will be parsed as `OPTIMADEUrl` instances without any changes.
        - Nothing else will pass validation
        - Serialization will always return just a str.
        """
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.url_schema(
                    max_length=cls.max_length,
                    host_required=cls.host_required,
                    allowed_schemes=cls.allowed_schemes,
                ),
                core_schema.no_info_plain_validator_function(
                    cls._validate_from_str_or_url
                ),
            ],
        )

        from_url_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(Url),
                core_schema.no_info_plain_validator_function(
                    cls._validate_from_str_or_url
                ),
            ],
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    from_url_schema,
                    from_str_schema,
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for an AnyHttpUrl
        return handler(
            core_schema.url_schema(
                max_length=cls.max_length,
                host_required=cls.host_required,
                allowed_schemes=cls.allowed_schemes,
            )
        )

    @classmethod
    def _validate_from_str_or_url(cls, value: Union[Url, str]) -> OPTIMADEUrl:
        """Pydantic validation of an OPTIMADE URL."""
        # Parse as URL
        url = AnyHttpUrl(str(value))

        # Build OPTIMADE URL parts
        optimade_parts = cls._build_optimade_parts(url)

        return cls(  # type: ignore[no-any-return]
            None,
            base_url=optimade_parts["base_url"],
            version=optimade_parts["version"],
            endpoint=optimade_parts["endpoint"],
            query=optimade_parts["query"],
        )

    @classmethod
    def _build_optimade_parts(cls, url: AnyHttpUrl) -> OPTIMADEParts:
        """Convert URL parts to equivalent OPTIMADE URL parts."""
        base_url = f"{url.scheme}://"

        if url.username:
            base_url += url.username

        if url.password:
            base_url += f":{url.password}"

        if url.username and url.password:
            base_url += "@"

        # This check is done to satisfy type checker.
        # Since the url has been parsed as a `AnyHttpUrl`, it must always have a host.
        if url.host is None:
            error_message = "Could not parse given string as a URL."
            raise ValueError(error_message)

        base_url += url.host

        # Hide port if it's a standard HTTP (80) or HTTPS (443) port.
        if url.port and url.port not in (80, 443):
            base_url += f":{url.port}"

        if url.path:
            base_url += url.path

        base_url_match = _OPTIMADE_BASE_URL_REGEX.fullmatch(base_url)
        LOGGER.debug(
            "OPTIMADE base URL regex match groups: %s",
            base_url_match.groupdict() if base_url_match else base_url_match,
        )
        if base_url_match is None:
            error_message = "Could not match given string with OPTIMADE base URL regex."
            raise ValueError(error_message)

        endpoint_match = _OPTIMADE_ENDPOINT_REGEX.findall(
            base_url_match.group("path") if base_url_match.group("path") else ""
        )
        LOGGER.debug("OPTIMADE endpoint regex matches: %s", endpoint_match)
        for path_version, path_endpoint in endpoint_match:  # noqa: B007
            if path_endpoint:
                break
        else:
            LOGGER.debug("Could not match given string with OPTIMADE endpoint regex.")
            path_version, path_endpoint = "", ""

        base_url = base_url_match.group("base_url")
        if path_version:
            base_url = base_url[: -(len(path_version) + len(path_endpoint) + 2)]
        elif path_endpoint:
            base_url = base_url[: -(len(path_endpoint) + 1)]

        optimade_parts = {
            "base_url": base_url.rstrip("/"),
            "version": path_version or None,
            "endpoint": path_endpoint or None,
            "query": url.query,
        }
        return cast("OPTIMADEParts", optimade_parts)

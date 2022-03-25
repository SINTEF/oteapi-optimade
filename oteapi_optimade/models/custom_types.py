"""Custom "pydantic" types used in OTEAPI-OPTIMADE."""
import logging
import re
from typing import TYPE_CHECKING, cast, no_type_check
from urllib.parse import quote as urlquote
from urllib.parse import urlparse, urlunparse

from pydantic import AnyUrl
from pydantic.networks import ascii_domain_regex, errors, int_domain_regex, url_regex
from pydantic.utils import update_not_none
from pydantic.validators import constr_length_validator, str_validator

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Pattern, Tuple, TypedDict

    from pydantic.config import BaseConfig
    from pydantic.fields import ModelField
    from pydantic.networks import CallableGenerator, Parts

    class OPTIMADEParts(TypedDict, total=False):
        """Similar to `pydantic.networks.Parts`."""

        base_url: AnyUrl
        version: Optional[str]
        endpoint: Optional[str]
        query: Optional[str]


_OPTIMADE_BASE_URL_REGEX = None

LOGGER = logging.getLogger("oteapi_optimade.models")
LOGGER.setLevel(logging.DEBUG)


def optimade_base_url_regex() -> "Pattern[str]":
    """A regular expression for an OPTIMADE base URL."""
    global _OPTIMADE_BASE_URL_REGEX  # pylint: disable=global-statement
    if _OPTIMADE_BASE_URL_REGEX is None:
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
            r"(?:/[^\s?#]*)?"  # path
            r")"
            r"(?:/(?P<version>v[0-9]+(?:\.[0-9+]){0,2}))?"  # version
            # endpoint
            r"(?:/(?P<endpoint>(?:info|links|versions|structures|references"
            r"|calculations|extensions)(?:/[^\s?#]*)?))?$",
            re.IGNORECASE,
        )
    return _OPTIMADE_BASE_URL_REGEX


class OPTIMADEUrl(str):
    """A deconstructed OPTIMADE URL.

    An OPTIMADE URL is made up in the following way:

        <BASE URL>/[<VERSION>/]<ENDPOINT>?<QUERY PARAMETERS>

    Where parts in square brackets (`[]`) are optional.
    """

    strip_whitespace = True
    min_length = 1
    # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers  # pylint: disable=line-too-long
    max_length = 2083
    allowed_schemes = {"http", "https"}
    tld_required = False
    user_required = False

    __slots__ = ("base_url", "version", "endpoint", "query", "tld", "host_type")

    @no_type_check
    def __new__(
        cls, url: "Optional[str]" = None, base_url: "Optional[AnyUrl]" = None, **kwargs
    ) -> object:
        return str.__new__(
            cls, cls.build(base_url=base_url, **kwargs) if url is None else url
        )

    def __init__(
        self,
        url: str,
        *,
        base_url: "Optional[AnyUrl]" = None,
        version: "Optional[str]" = None,
        endpoint: "Optional[str]" = None,
        query: "Optional[str]" = None,
        tld: "Optional[str]" = None,
        host_type: str = "domain",
    ) -> None:
        str.__init__(url)
        self.base_url = base_url
        self.version = version
        self.endpoint = endpoint
        self.query = query
        self.tld = tld
        self.host_type = host_type

    @classmethod
    def build(
        cls,
        *,
        base_url: "AnyUrl",
        version: "Optional[str]" = None,
        endpoint: "Optional[str]" = None,
        query: "Optional[str]" = None,
        **_kwargs: str,
    ) -> str:
        """Build complete URL from URL parts."""
        url = str(base_url).rstrip("/")
        if version:
            url += f"/{version}"
        if endpoint:
            url += f"/{endpoint}"
        if query:
            url += f"?{query}"
        return url

    @classmethod
    def __modify_schema__(cls, field_schema: "Dict[str, Any]") -> None:
        update_not_none(
            field_schema,
            minLength=cls.min_length,
            maxLength=cls.max_length,
            format="uri",
        )

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @staticmethod
    def urlquote_qs(url: str) -> str:
        """Use `urllib.parse.quote` for query part of URL."""
        parsed_url = urlparse(url)
        quoted_query = urlquote(parsed_url.query, safe="=&,")
        parsed_url_list = list(parsed_url)
        parsed_url_list[-2] = quoted_query
        return urlunparse(parsed_url_list)

    @classmethod
    def validate(
        cls, value: "Any", field: "ModelField", config: "BaseConfig"
    ) -> "OPTIMADEUrl":
        """Pydantic validation of an OPTIMADE URL."""
        if value.__class__ == cls:
            return value

        value: str = str_validator(value)
        if cls.strip_whitespace:
            value = value.strip()
        url: str = cast(str, constr_length_validator(value, field, config))
        url = cls.urlquote_qs(url)

        url_match = url_regex().match(url)
        if url_match is None:
            raise ValueError(f"Cannot match URL ({url!r}) as a valid URL.")

        parts = cast("Parts", url_match.groupdict())
        parts = cls.apply_default_parts(parts)
        host, tld, host_type, rebuild = cls.validate_host(parts)
        optimade_parts = cls.build_optimade_parts(parts, host)
        optimade_parts = cls.validate_parts(parts, optimade_parts)

        if url_match.end() != len(url):
            raise errors.UrlExtraError(extra=url[url_match.end() :])

        return cls(
            None if rebuild else url,
            base_url=optimade_parts["base_url"],
            version=optimade_parts["version"],
            endpoint=optimade_parts["endpoint"],
            query=optimade_parts["query"],
            tld=tld,
            host_type=host_type,
        )

    @classmethod
    def validate_host(cls, parts: "Parts") -> "Tuple[str, Optional[str], str, bool]":
        """Validate host-part of the URL."""
        host: "Optional[str]" = None
        tld: "Optional[str]" = None
        rebuild: bool = False
        for host_type in ("domain", "ipv4", "ipv6"):
            host = parts[host_type]  # type: ignore[misc]
            if host:
                break
        else:
            raise errors.UrlHostError()

        if host_type == "domain":
            is_international = False
            domain = ascii_domain_regex().fullmatch(host)
            if domain is None:
                domain = int_domain_regex().fullmatch(host)
                if domain is None:
                    raise errors.UrlHostError()
                is_international = True

            tld = domain.group("tld")
            if tld is None and not is_international:
                domain = int_domain_regex().fullmatch(host)
                if domain is None:
                    raise ValueError("domain cannot be None")
                tld = domain.group("tld")
                is_international = True

            if tld is not None:
                tld = tld[1:]
            elif cls.tld_required:
                raise errors.UrlHostTldError()

            if is_international:
                host_type = "int_domain"
                rebuild = True
                host = host.encode("idna").decode("ascii")
                if tld is not None:
                    tld = tld.encode("idna").decode("ascii")

        return host, tld, host_type, rebuild

    @staticmethod
    def get_default_parts(parts: "Parts") -> "Parts":
        """Dictionary of default URL-part values."""
        return {"port": "80" if parts["scheme"] == "http" else "443"}

    @classmethod
    def apply_default_parts(cls, parts: "Parts") -> "Parts":
        """Apply default URL-part values if no value is given."""
        for key, value in cls.get_default_parts(parts).items():
            if not parts[key]:  # type: ignore[misc]
                parts[key] = value  # type: ignore[misc]
        return parts

    @classmethod
    def build_optimade_parts(cls, parts: "Parts", host: str) -> "OPTIMADEParts":
        """Convert URL parts to equivalent OPTIMADE URL parts."""

        base_url = f"{parts['scheme']}://"
        if parts["user"]:
            base_url += parts["user"]
        if parts["password"]:
            base_url += f":{parts['password']}"
        if parts["user"] or parts["password"]:
            base_url += "@"
        base_url += host
        # Hide port if it's a standard HTTP (80) or HTTPS (443) port.
        if parts["port"] and parts["port"] not in ("80", "443"):
            base_url += f":{parts['port']}"
        if parts["path"]:
            base_url += parts["path"]

        match = optimade_base_url_regex().fullmatch(base_url)
        LOGGER.debug(
            "OPTIMADE URL regex match groups: %s", match.groupdict() if match else match
        )
        if match is None:
            raise ValueError("Could not match given string with OPTIMADE regex.")

        optimade_parts = {
            "base_url": match.group("base_url"),
            "version": match.group("version"),
            "endpoint": match.group("endpoint"),
            "query": parts["query"],
        }
        return cast("OPTIMADEParts", optimade_parts)

    @classmethod
    def validate_parts(
        cls, parts: "Parts", optimade_parts: "OPTIMADEParts"
    ) -> "OPTIMADEParts":
        """
        A method used to validate parts of an URL.
        Could be overridden to set default values for parts if missing
        """
        scheme = parts["scheme"]
        if scheme is None:
            raise errors.UrlSchemeError()

        if cls.allowed_schemes and scheme.lower() not in cls.allowed_schemes:
            raise errors.UrlSchemePermittedError(set(cls.allowed_schemes))

        port = parts["port"]
        if port is not None and int(port) > 65_535:
            raise errors.UrlPortError()

        user = parts["user"]
        if cls.user_required and user is None:
            raise errors.UrlUserInfoError()

        base_url = optimade_parts["base_url"]
        if base_url is None:
            raise errors.UrlError()

        return optimade_parts

    def __repr__(self) -> str:
        extra = ", ".join(
            f"{n}={getattr(self, n)!r}"
            for n in self.__slots__
            if getattr(self, n) is not None
        )
        return f"{self.__class__.__name__}({super().__repr__()}, {extra})"

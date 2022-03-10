"""OTE-API OPTIMADE-specific Python exceptions."""


class BaseOteapiOptimadeException(Exception):
    """Base OTE-API OPTIMADE exception."""


class ConfigurationError(BaseOteapiOptimadeException):
    """An error occurred when dealing with strategy configurations."""


class InconsistentBaseUrl(ConfigurationError):
    """Inconsistent base URL.

    The provided [base URL][oteapi_optimade.models.config.OPTIMADEConfig.base_url] is
    inconsistent with the provided
    [`accessUrl`][oteapi_optimade.models.resource.OPTIMADEResourceConfig.accessUrl].
    """


class RequestError(BaseOteapiOptimadeException):
    """A general error occured when performing a URL request."""


class OPTIMADEResponseError(RequestError):
    """An OPTIMADE error was returned from a URL request."""


class OPTIMADEParseError(BaseOteapiOptimadeException):
    """Could not use OPTIMADE Python tools to parse an OPTIMADE API response."""

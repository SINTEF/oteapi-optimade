"""OTE-API OPTIMADE-specific Python exceptions."""

from __future__ import annotations


class BaseOteapiOptimadeException(Exception):
    """Base OTE-API OPTIMADE exception."""


class MissingDependency(BaseOteapiOptimadeException):
    """A required dependency is missing."""


class ConfigurationError(BaseOteapiOptimadeException):
    """An error occurred when dealing with strategy configurations."""


class RequestError(BaseOteapiOptimadeException):
    """A general error occured when performing a URL request."""


class OPTIMADEResponseError(RequestError):
    """An OPTIMADE error was returned from a URL request."""


class OPTIMADEParseError(BaseOteapiOptimadeException):
    """Could not use OPTIMADE Python tools to parse an OPTIMADE API response."""

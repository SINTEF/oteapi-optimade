"""Models specific to the filter strategy."""
from typing import Any, Dict, Literal, Optional

from optimade.models import Response
from oteapi.models import FilterConfig, SessionUpdate
from pydantic import Field

from oteapi_optimade.models.config import OPTIMADEConfig


class OPTIMADEFilterConfig(FilterConfig):
    """OPTIMADE-specific filter strategy config.

    Note:
        The `condition` parameter is not taken into account.

    """

    filterType: Literal["optimade", "OPTIMADE", "OPTiMaDe"] = Field(
        ...,
        description="The registered strategy name for OPTIMADEFilterStrategy.",
    )
    query: Optional[str] = Field(
        None,
        description=(
            "The `filter` OPTIMADE query parameter value. This parameter value can "
            "also be provided through the [`configuration.query_parameters.filter`]"
            "[oteapi_optimade.models.query.OPTIMADEQueryParameters.filter] parameter. "
            "Note, this value takes precedence over [`configuration`][oteapi_optimade."
            "models.strategies.filter.OPTIMADEFilterConfig.configuration] values."
        ),
    )
    limit: Optional[int] = Field(
        None,
        description=(
            "The `page_limit` OPTIMADE query parameter value. This parameter value can"
            " also be provided through the [`configuration.query_parameters."
            "page_limit`][oteapi_optimade.models.query.OPTIMADEQueryParameters."
            "page_limit] parameter. Note, this value takes precedence over "
            "[`configuration`][oteapi_optimade.models.strategies.filter."
            "OPTIMADEFilterConfig.configuration] values."
        ),
    )
    configuration: OPTIMADEConfig = Field(
        OPTIMADEConfig(),
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )


class OPTIMADEFilterSession(SessionUpdate):
    """OPTIMADE session for the filter strategy."""

    optimade_config: Optional[OPTIMADEConfig] = Field(
        None,
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )
    optimade_response_object: Optional[Response] = Field(
        None,
        description="An OPTIMADE Python tools (OPT) pydantic response object.",
    )
    optimade_response: Optional[Dict[str, Any]] = Field(
        None,
        description="An OPTIMADE response as a Python dictionary.",
    )

    class Config:
        """Pydantic configuration for `OPTIMADEFilterSession`."""

        validate_assignment = True
        arbitrary_types_allowed = True

"""Models specific to the filter strategy."""
from typing import Any, Dict, Literal, Optional, Annotated

from optimade.models import Response
from oteapi.models import FilterConfig, SessionUpdate
from pydantic import ConfigDict, Field

from oteapi_optimade.models.config import OPTIMADEConfig


class OPTIMADEFilterConfig(FilterConfig):
    """OPTIMADE-specific filter strategy config.

    Note:
        The `condition` parameter is not taken into account.

    """

    filterType: Annotated[
        Literal["optimade", "OPTIMADE", "OPTiMaDe"],
        Field(
            description="The registered strategy name for OPTIMADEFilterStrategy.",
        ),
    ]
    query: Annotated[
        Optional[str],
        Field(
            description=(
                "The `filter` OPTIMADE query parameter value. This parameter value can "
                "also be provided through the [`configuration.query_parameters.filter`]"
                "[oteapi_optimade.models.query.OPTIMADEQueryParameters.filter] parameter. "
                "Note, this value takes precedence over [`configuration`][oteapi_optimade."
                "models.strategies.filter.OPTIMADEFilterConfig.configuration] values."
            ),
        ),
    ] = None
    limit: Annotated[
        Optional[int],
        Field(
            description=(
                "The `page_limit` OPTIMADE query parameter value. This parameter value can"
                " also be provided through the [`configuration.query_parameters."
                "page_limit`][oteapi_optimade.models.query.OPTIMADEQueryParameters."
                "page_limit] parameter. Note, this value takes precedence over "
                "[`configuration`][oteapi_optimade.models.strategies.filter."
                "OPTIMADEFilterConfig.configuration] values."
            ),
        ),
    ] = None
    configuration: Annotated[
        OPTIMADEConfig,
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = OPTIMADEConfig()


class OPTIMADEFilterSession(SessionUpdate):
    """OPTIMADE session for the filter strategy."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    optimade_config: Annotated[
        Optional[OPTIMADEConfig],
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = None
    optimade_response_object: Annotated[
        Optional[Response],
        Field(
            description="An OPTIMADE Python tools (OPT) pydantic response object.",
        ),
    ] = None
    optimade_response: Annotated[
        Optional[Dict[str, Any]],
        Field(
            description="An OPTIMADE response as a Python dictionary.",
        ),
    ] = None

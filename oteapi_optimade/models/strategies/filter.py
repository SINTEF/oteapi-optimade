"""Models specific to the filter strategy."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from oteapi.models import AttrDict, FilterConfig
from pydantic import BeforeValidator, ConfigDict, Field

from oteapi_optimade.models.config import OPTIMADEConfig


class OPTIMADEFilterConfig(FilterConfig):
    """OPTIMADE-specific filter strategy config.

    Note:
        The `condition` parameter is not taken into account.

    """

    filterType: Annotated[
        Literal["optimade"],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(
            description="The registered strategy name for OPTIMADEFilterStrategy.",
        ),
    ]
    query: Annotated[
        str | None,
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
        int | None,
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


class OPTIMADEFilterResult(AttrDict):
    """OPTIMADE session for the filter strategy."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    optimade_config: Annotated[
        OPTIMADEConfig | None,
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = None
    optimade_response_model: Annotated[
        tuple[str, str] | None,
        Field(
            description=(
                "An OPTIMADE Python tools (OPT) pydantic successful response model. "
                "More specifically, a tuple of the module and name of the pydantic "
                "model."
            ),
        ),
    ] = None
    optimade_response: Annotated[
        dict[str, Any] | None,
        Field(
            description="An OPTIMADE response as a Python dictionary.",
        ),
    ] = None

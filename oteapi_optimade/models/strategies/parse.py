"""Models specific to the parse strategy."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional

from oteapi.models import ResourceConfig, SessionUpdate
from pydantic import ConfigDict, Field

from oteapi_optimade.models.config import OPTIMADEConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl


class OPTIMADEParseConfig(ResourceConfig):  # type: ignore[misc]
    """OPTIMADE-specific parse strategy config."""

    downloadUrl: Annotated[
        OPTIMADEUrl,
        Field(
            description="Either a base OPTIMADE URL or a full OPTIMADE URL.",
        ),
    ]
    mediaType: Annotated[
        Literal[
            "application/vnd.optimade+json",
            "application/vnd.OPTIMADE+json",
            "application/vnd.OPTiMaDe+json",
            "application/vnd.optimade+JSON",
            "application/vnd.OPTIMADE+JSON",
            "application/vnd.OPTiMaDe+JSON",
            "application/vnd.optimade",
            "application/vnd.OPTIMADE",
            "application/vnd.OPTiMaDe",
        ],
        Field(
            description="The registered strategy name for OPTIMADEParseStrategy.",
        ),
    ]
    configuration: Annotated[
        OPTIMADEConfig,
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = OPTIMADEConfig()


class OPTIMADEParseSession(SessionUpdate):  # type: ignore[misc]
    """OPTIMADE session for the parse strategy."""

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
    optimade_response_model: Annotated[
        Optional[tuple[str, str]],
        Field(
            description=(
                "An OPTIMADE Python tools (OPT) pydantic successful response model. "
                "More specifically, a tuple of the module and name of the pydantic "
                "model."
            ),
        ),
    ] = None
    optimade_response: Annotated[
        Optional[dict[str, Any]],
        Field(
            description="An OPTIMADE response as a Python dictionary.",
        ),
    ] = None


class OPTIMADEDLiteParseConfig(OPTIMADEParseConfig):
    """OPTIMADE-specific parse strategy config."""

    mediaType: Annotated[  # type: ignore[assignment]
        Literal[
            "application/vnd.optimade+dlite",
            "application/vnd.OPTIMADE+dlite",
            "application/vnd.OPTiMaDe+dlite",
            "application/vnd.optimade+DLite",
            "application/vnd.OPTIMADE+DLite",
            "application/vnd.OPTiMaDe+DLite",
        ],
        Field(
            description="The registered strategy name for OPTIMADEDLiteParseStrategy.",
        ),
    ]

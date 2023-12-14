"""Models specific to the parse strategy."""
from __future__ import annotations

from typing import Any, Literal, Optional

from optimade.models import Response
from oteapi.models import ResourceConfig, SessionUpdate
from pydantic import Field

from oteapi_optimade.models.config import OPTIMADEConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl


class OPTIMADEParseConfig(ResourceConfig):  # type: ignore[misc]
    """OPTIMADE-specific parse strategy config."""

    downloadUrl: OPTIMADEUrl = Field(
        ...,
        description="Either a base OPTIMADE URL or a full OPTIMADE URL.",
    )
    mediaType: Literal[
        "application/vnd.optimade+json",
        "application/vnd.OPTIMADE+json",
        "application/vnd.OPTiMaDe+json",
        "application/vnd.optimade+JSON",
        "application/vnd.OPTIMADE+JSON",
        "application/vnd.OPTiMaDe+JSON",
        "application/vnd.optimade",
        "application/vnd.OPTIMADE",
        "application/vnd.OPTiMaDe",
    ] = Field(
        ...,
        description="The registered strategy name for OPTIMADEParseStrategy.",
    )
    configuration: OPTIMADEConfig = Field(
        OPTIMADEConfig(),
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )


class OPTIMADEParseSession(SessionUpdate):  # type: ignore[misc]
    """OPTIMADE session for the parse strategy."""

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
    optimade_response: Optional[dict[str, Any]] = Field(
        None,
        description="An OPTIMADE response as a Python dictionary.",
    )

    class Config:
        """Pydantic configuration for `OPTIMADEParseSession`."""

        validate_assignment = True
        arbitrary_types_allowed = True


class OPTIMADEDLiteParseConfig(OPTIMADEParseConfig):
    """OPTIMADE-specific parse strategy config."""

    mediaType: Literal[
        "application/vnd.optimade+dlite",
        "application/vnd.OPTIMADE+dlite",
        "application/vnd.OPTiMaDe+dlite",
        "application/vnd.optimade+DLite",
        "application/vnd.OPTIMADE+DLite",
        "application/vnd.OPTiMaDe+DLite",
    ] = Field(  # type: ignore[assignment]
        ...,
        description="The registered strategy name for OPTIMADEDLiteParseStrategy.",
    )

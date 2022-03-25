"""Models specific to the parse strategy."""
# pylint: disable=no-self-use
from typing import Any, Dict, Literal, Optional, Union

from optimade.models import Response
from oteapi.models import ResourceConfig, SessionUpdate
from pydantic import Field, validator

from oteapi_optimade.models.config import OPTIMADEConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl


class OPTIMADEParseConfig(ResourceConfig):
    """OPTIMADE-specific parse strategy config."""

    downloadUrl: OPTIMADEUrl = Field(
        ...,
        description="Either a base OPTIMADE URL or a full OPTIMADE URL.",
    )
    mediaType: Union[
        Literal["application/vnd.optimade+json"],
        Literal["application/vnd.OPTIMADE+json"],
        Literal["application/vnd.OPTiMaDe+json"],
        Literal["application/vnd.optimade+JSON"],
        Literal["application/vnd.OPTIMADE+JSON"],
        Literal["application/vnd.OPTiMaDe+JSON"],
        Literal["application/vnd.optimade"],
        Literal["application/vnd.OPTIMADE"],
        Literal["application/vnd.OPTiMaDe"],
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

    @validator("configuration", allow_reuse=True)
    def check_base_url(
        cls, value: OPTIMADEConfig, values: "Dict[str, Any]"
    ) -> OPTIMADEConfig:
        """Check that `configuration.base_url` is a sub-set of `downloadUrl`."""
        if value.base_url and str(value.base_url) not in str(
            values.get("downloadUrl", "")
        ):
            raise ValueError(
                f"`configuration.base_url` ({value.base_url}) must be a sub-set of "
                f"`downloadUrl` {values.get('downloadUrl', '')}."
            )
        return value

    class Config:
        """Pydantic configuration for `OPTIMADEParseConfig`."""

        allow_reuse = True


class OPTIMADEParseSession(SessionUpdate):
    """OPTIMADE session for the resource strategy."""

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
        """Pydantic configuration for `OPTIMADEParseSession`."""

        validate_assignment = True
        arbitrary_types_allowed = True

"""Models specific to the resource strategy."""
# pylint: disable=no-self-use
from typing import TYPE_CHECKING, List, Literal, Optional, Union

from optimade.adapters import Reference, Structure
from optimade.models import OptimadeError
from oteapi.models import ResourceConfig, SessionUpdate
from pydantic import Field, validator

from oteapi_optimade.models.config import OPTIMADEConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl

if TYPE_CHECKING:
    from typing import Any, Dict


class OPTIMADEResourceConfig(ResourceConfig):
    """OPTIMADE-specific resource strategy config."""

    accessUrl: OPTIMADEUrl = Field(
        ...,
        description="Either a base OPTIMADE URL or a full OPTIMADE URL.",
    )
    accessService: Union[
        Literal["optimade"], Literal["OPTIMADE"], Literal["OPTiMaDe"]
    ] = Field(
        ...,
        description="The registered strategy name for OPTIMADEResourceStrategy.",
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
        """Check that `configuration.base_url` is a sub-set of `accessUrl`."""
        if value.base_url and str(value.base_url) not in str(
            values.get("accessUrl", "")
        ):
            raise ValueError(
                f"`configuration.base_url` ({value.base_url}) must be a sub-set of "
                f"`accessUrl` {values.get('accessUrl', '')}."
            )
        return value

    class Config:
        """Pydantic configuration for `OPTIMADEResourceConfig`."""

        allow_reuse = True


class OPTIMADEResourceSession(SessionUpdate):
    """OPTIMADE session for the resource strategy."""

    optimade_config: Optional[OPTIMADEConfig] = Field(
        None,
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )
    optimade_errors: List[OptimadeError] = Field(
        [],
        description="List of errors returned from the OPTIMADE request.",
    )
    optimade_structures: List[Structure] = Field(
        [],
        description="List of OPTIMADE structures.",
    )
    optimade_references: List[Reference] = Field(
        [],
        description="List of OPTIMADE references.",
    )

    class Config:
        """Pydantic configuration for `OPTIMADEResourceSession`."""

        validate_assignment = True
        arbitrary_types_allowed = True

"""Models specific to the resource strategy."""
# pylint: disable=no-self-use
from typing import TYPE_CHECKING

from oteapi.models import ResourceConfig
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
    accessService: str = Field(
        "optimade",
        const=True,
        description="The registered strategy name for OPTIMADEResourceStrategy.",
    )
    configuration: OPTIMADEConfig = Field(
        OPTIMADEConfig(),
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )

    @validator("configuration")
    def check_base_url(
        cls, value: OPTIMADEConfig, values: "Dict[str, Any]"
    ) -> OPTIMADEConfig:
        """Check that `configuration.base_url` is a sub-set of `accessUrl`."""
        if not value.base_url:
            pass
        elif str(value.base_url) not in str(values.get("accessUrl", "")):
            raise ValueError(
                f"`configuration.base_url` ({value.base_url}) must be a sub-set of "
                f"`accessUrl` {values.get('accessUrl', '')}."
            )
        return value

"""General OPTIMADE configuration models."""
from typing import Literal, Optional

from oteapi.models import AttrDict, DataCacheConfig
from pydantic import Field, validator

from oteapi_optimade.models.query import OPTIMADEQueryParameters

DEFAULT_CACHE_CONFIG_VALUES = {
    "expireTime": 60 * 60 * 24,  # 1 day (in seconds) = 60 s/min * 60 min/h * 24 h/day
    "tag": "optimade",
}
"""Set the `expireTime` and `tag` to default values for the data cache."""


class OPTIMADEConfig(AttrDict):
    """OPTIMADE configuration."""

    version: str = Field(
        "v1",
        description="The version part of the OPTIMADE versioned base URL.",
        regex=r"^v[0-9]+(\.[0-9]+){,2}$",
    )
    endpoint: Literal["references", "structures"] = Field(
        "structures",
        description="Supported OPTIMADE entry resource endpoint.",
    )
    query_parameters: Optional[OPTIMADEQueryParameters] = Field(
        None,
        description="URL query parameters to be used in the OPTIMADE query.",
    )
    datacache_config: DataCacheConfig = Field(
        DataCacheConfig(**DEFAULT_CACHE_CONFIG_VALUES),
        description="Configuration options for the local data cache.",
    )
    return_object: bool = Field(
        False,
        description=(
            "Whether or not to return a response object (using the pydantic model).\n"
            "\nImportant:\n    This should _only_ be used if the strategy is called "
            "directly and not via an OTEAPI REST API service."
        ),
    )

    @validator("datacache_config")
    def default_datacache_config(cls, value: DataCacheConfig) -> DataCacheConfig:
        """Use default values for `DataCacheConfig` if not supplied."""
        original_set_values = len(value.__fields_set__)

        for field, default_value in DEFAULT_CACHE_CONFIG_VALUES.items():
            if field in value.__fields_set__:
                # Use the set value instead of the default
                continue
            setattr(value, field, default_value)

        if len(value.__fields_set__) > original_set_values:
            # Re-validate model and return it
            return value.validate(
                {
                    field: field_value
                    for field, field_value in value.dict().items()
                    if field in value.__fields_set__
                }
            )
        return value

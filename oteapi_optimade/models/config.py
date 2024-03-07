"""General OPTIMADE configuration models."""

from __future__ import annotations

from typing import Annotated, Literal, Optional

from oteapi.models import AttrDict, DataCacheConfig
from pydantic import Field, field_validator

from oteapi_optimade.models.query import OPTIMADEQueryParameters

DEFAULT_CACHE_CONFIG_VALUES = {
    "expireTime": 60 * 60 * 24,  # 1 day (in seconds) = 60 s/min * 60 min/h * 24 h/day
    "tag": "optimade",
}
"""Set the `expireTime` and `tag` to default values for the data cache."""


class OPTIMADEConfig(AttrDict):  # type: ignore[misc]
    """OPTIMADE configuration."""

    version: Annotated[
        str,
        Field(
            description="The version part of the OPTIMADE versioned base URL.",
            pattern=r"^v[0-9]+(\.[0-9]+){0,2}$",
        ),
    ] = "v1"
    endpoint: Annotated[
        Literal["references", "structures"],
        Field(
            description="Supported OPTIMADE entry resource endpoint.",
        ),
    ] = "structures"
    query_parameters: Annotated[
        Optional[OPTIMADEQueryParameters],
        Field(
            description="URL query parameters to be used in the OPTIMADE query.",
        ),
    ] = None
    datacache_config: Annotated[
        DataCacheConfig,
        Field(
            description="Configuration options for the local data cache.",
        ),
    ] = DataCacheConfig(**DEFAULT_CACHE_CONFIG_VALUES)
    use_dlite: Annotated[
        bool,
        Field(
            description="Whether or not to store the results in a DLite Collection.",
        ),
    ] = False

    @field_validator("datacache_config", mode="after")
    @classmethod
    def default_datacache_config(
        cls, datacache_config: DataCacheConfig
    ) -> DataCacheConfig:
        """Use default values for `DataCacheConfig` if not supplied."""
        original_set_values = len(datacache_config.model_fields_set)

        for field, default_value in DEFAULT_CACHE_CONFIG_VALUES.items():
            if field in datacache_config.model_fields_set:
                # Use the set value instead of the default
                continue
            setattr(datacache_config, field, default_value)

        if len(datacache_config.model_fields_set) > original_set_values:
            # Re-validate model and return it
            return datacache_config.model_validate(
                {
                    field: field_value
                    for field, field_value in datacache_config.model_dump().items()
                    if field in datacache_config.model_fields_set
                }
            )
        return datacache_config

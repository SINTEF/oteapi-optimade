"""General OPTIMADE configuration models."""
# pylint: disable=no-self-use
from typing import Optional

from oteapi.models import AttrDict, DataCacheConfig
from pydantic import Field, validator

from oteapi_optimade.models.custom_types import OPTIMADEUrl
from oteapi_optimade.models.query import OPTIMADEQueryParameters

DEFAULT_CACHE_CONFIG_VALUES = {
    "expireTime": 60 * 60 * 24,  # 1 day (in seconds) = 60 s/min * 60 min/h * 24 h/day
    "tag": "optimade",
}
"""Set the `expireTime` and `tag` to default values for the data cache."""


class OPTIMADEConfig(AttrDict):
    """OPTIMADE configuration."""

    base_url: Optional[OPTIMADEUrl] = Field(
        None,
        description=(
            "Base OPTIMADE URL. Must be a sub-part of the provided `accessUrl`. If not"
            " provided, it is assumed `accessUrl` is either complete or an OPTIMADE "
            "base URL itself."
        ),
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
            "Whether or not to return a response object (using the pydantic model)."
        ),
    )

    @validator("base_url")
    def check_base_url(cls, value: OPTIMADEUrl) -> OPTIMADEUrl:
        """Make sure `base_url` is just the base URL."""
        if str(value) != value.base_url:
            return OPTIMADEUrl(value.base_url, base_url=value.base_url)
        return value

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

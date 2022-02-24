"""Demo strategy class for text/json."""
# pylint: disable=no-self-use,unused-argument
import json
from typing import TYPE_CHECKING, Optional

from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, ResourceConfig, SessionUpdate
from oteapi.plugins import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict


class JSONConfig(AttrDict):
    """JSON parse-specific Configuration Data Model."""

    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )


class JSONParseConfig(ResourceConfig):
    """File download strategy filter config."""

    configuration: JSONConfig = Field(
        JSONConfig(), description="JSON parse strategy-specific configuration."
    )


class SessionUpdateJSONParse(SessionUpdate):
    """Class for returning values from JSON Parse."""

    content: dict = Field(..., description="Content of the JSON document.")


@dataclass
class DemoJSONDataParseStrategy:
    """Parse strategy for JSON.

    **Registers strategies**:

    - `("mediaType", "application/jsonDEMO")`

    """

    parse_config: JSONParseConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize."""
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdateJSONParse:
        """Parse json."""
        downloader = create_strategy("download", self.parse_config)
        output = downloader.get()
        cache = DataCache(self.parse_config.configuration.datacache_config)
        content = cache.get(output["key"])

        if isinstance(content, dict):
            return SessionUpdateJSONParse(content=content)
        return SessionUpdateJSONParse(content=json.loads(content))

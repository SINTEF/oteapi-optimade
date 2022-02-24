"""Demo mapping strategy class."""
# pylint: disable=no-self-use,unused-argument
from typing import TYPE_CHECKING

from oteapi.models import MappingConfig, SessionUpdate
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


@dataclass
class DemoMappingStrategy:
    """Mapping Strategy.

    **Registers strategies**:

    - `("mappingType", "mapping/DEMO")`

    """

    mapping_config: MappingConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return SessionUpdate()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> SessionUpdate:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return SessionUpdate()

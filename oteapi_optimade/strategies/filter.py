"""Demo filter strategy."""
# pylint: disable=no-self-use,unused-argument
from typing import TYPE_CHECKING, List

from oteapi.models import AttrDict, FilterConfig, SessionUpdate
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


class DemoDataModel(AttrDict):
    """Demo filter data model."""

    demo_data: List[int] = Field([], description="List of demo data.")


class DemoFilterConfig(FilterConfig):
    """Demo filter strategy filter config."""

    configuration: DemoDataModel = Field(
        DemoDataModel(), description="Demo filter data model."
    )


class SessionUpdateDemoFilter(SessionUpdate):
    """Class for returning values from Download File strategy."""

    key: str = Field(..., description="Key to access the data in the cache.")


@dataclass
class OPTIMADEFilterStrategy:
    """Filter Strategy.

    **Implements strategies**:

    - `("filterType", "OPTIMADE")`
    - `("filterType", "optimade")`
    - `("filterType", "OPTiMaDe")`

    """

    filter_config: DemoFilterConfig

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

    def get(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> SessionUpdateDemoFilter:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return SessionUpdateDemoFilter(key=self.filter_config.configuration.demo_data)

"""Demo resource strategy class."""
# pylint: disable=no-self-use,unused-argument
from typing import TYPE_CHECKING

from oteapi.models import ResourceConfig, SessionUpdate
from oteapi.plugins import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


class SessionUpdateDemoResource(SessionUpdate):
    """Class for returning values from Demo Resource strategy."""

    output: dict = Field(
        ...,
        description=(
            "The output from downloading the response from the given `accessUrl`."
        ),
    )


@dataclass
class DemoResourceStrategy:
    """Resource Strategy.

    **Registers strategies**:

    - `("accessService", "DEMO-access-service")`

    """

    resource_config: ResourceConfig

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
    ) -> SessionUpdateDemoResource:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        # Example of the plugin using the download strategy to fetch the data
        download_strategy = create_strategy("download", self.resource_config)
        read_output = download_strategy.get(session)
        return SessionUpdateDemoResource(output=read_output.dict())

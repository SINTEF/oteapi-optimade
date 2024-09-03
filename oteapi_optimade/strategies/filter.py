"""Demo filter strategy."""

from __future__ import annotations

import logging

from oteapi.models import AttrDict
from pydantic.dataclasses import dataclass

from oteapi_optimade.models import OPTIMADEFilterConfig, OPTIMADEFilterResult
from oteapi_optimade.models.query import OPTIMADEQueryParameters

LOGGER = logging.getLogger(__name__)


@dataclass
class OPTIMADEFilterStrategy:
    """Filter Strategy.

    **Implements strategies**:

    - `("filterType", "OPTIMADE")`

    """

    filter_config: OPTIMADEFilterConfig

    def initialize(self) -> OPTIMADEFilterResult:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Configuration values, specifically URL query parameters, can be provided to the
        OPTIMADE resource strategy through this filter strategy.

        Workflow:

        1. Compile received information.
        2. Update session with compiled information.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        if self.filter_config.configuration.optimade_config:
            self.filter_config.configuration.update(
                self.filter_config.configuration.optimade_config.model_dump(
                    exclude_defaults=True,
                    exclude_unset=True,
                    exclude={"optimade_config", "downloadUrl", "mediaType"},
                )
            )

        optimade_config = self.filter_config.configuration.model_copy()

        if not optimade_config.query_parameters:
            optimade_config.query_parameters = OPTIMADEQueryParameters()

        if self.filter_config.query:
            LOGGER.debug("Setting filter from query.")
            optimade_config.query_parameters.filter = self.filter_config.query

        if self.filter_config.limit:
            LOGGER.debug("Setting page_limit from limit.")
            optimade_config.query_parameters.page_limit = self.filter_config.limit

        return OPTIMADEFilterResult(
            optimade_config=optimade_config.model_dump(
                exclude={"optimade_config", "downloadUrl", "mediaType"},
                exclude_unset=True,
                exclude_defaults=True,
            )
        )

    def get(self) -> AttrDict:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTE-API Services.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return AttrDict()

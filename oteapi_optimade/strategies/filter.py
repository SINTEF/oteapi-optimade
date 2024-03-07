"""Demo filter strategy."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from oteapi.models import SessionUpdate
from pydantic.dataclasses import dataclass

from oteapi_optimade.models import OPTIMADEFilterConfig, OPTIMADEFilterSession
from oteapi_optimade.models.query import OPTIMADEQueryParameters

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


LOGGER = logging.getLogger("oteapi_optimade.strategies")


@dataclass
class OPTIMADEFilterStrategy:
    """Filter Strategy.

    **Implements strategies**:

    - `("filterType", "OPTIMADE")`
    - `("filterType", "optimade")`
    - `("filterType", "OPTiMaDe")`

    """

    filter_config: OPTIMADEFilterConfig

    def initialize(
        self, session: SessionUpdate | dict[str, Any] | None = None
    ) -> OPTIMADEFilterSession:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTE-API
        Services.

        Configuration values, specifically URL query parameters, can be provided to the
        OPTIMADE resource strategy through this filter strategy.

        Workflow:

        1. Compile received information.
        2. Update session with compiled information.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        if session and isinstance(session, dict):
            session = OPTIMADEFilterSession(**session)
        elif session and isinstance(session, SessionUpdate):
            session = OPTIMADEFilterSession(
                **session.model_dump(exclude_defaults=True, exclude_unset=True)
            )
        else:
            session = OPTIMADEFilterSession()

        if session.optimade_config:
            self.filter_config.configuration.update(
                session.optimade_config.model_dump(
                    exclude_defaults=True, exclude_unset=True
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

        return session.model_copy(  # type: ignore[no-any-return]
            update={
                "optimade_config": optimade_config.model_copy(
                    update={
                        "query_parameters": optimade_config.query_parameters.model_dump(
                            exclude_defaults=True,
                            exclude_unset=True,
                        )
                    }
                )
            },
        )

    def get(
        self,
        session: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> SessionUpdate:
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

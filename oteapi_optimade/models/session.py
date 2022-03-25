"""General OPTIMADE session models."""
from typing import List, Optional

from optimade.adapters import Reference, Structure
from optimade.models import OptimadeError
from oteapi.models import SessionUpdate
from pydantic import Field

from oteapi_optimade.models.config import OPTIMADEConfig


class OPTIMADESession(SessionUpdate):
    """OPTIMADE session."""

    optimade_config: Optional[OPTIMADEConfig] = Field(
        None,
        description=(
            "OPTIMADE configuration. Contains relevant information necessary to "
            "perform OPTIMADE queries."
        ),
    )
    optimade_errors: List[OptimadeError] = Field(
        [],
        description="List of errors returned from the OPTIMADE request.",
    )
    optimade_structures: List[Structure] = Field(
        [],
        description="List of OPTIMADE structures.",
    )
    optimade_references: List[Reference] = Field(
        [],
        description="List of OPTIMADE references.",
    )

    class Config:
        """Pydantic configuration for `OPTIMADESession`."""

        validate_assignment = True
        arbitrary_types_allowed = True

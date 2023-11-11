"""Models specific to the resource strategy."""
from typing import Any, Dict, List, Literal, Optional, Annotated

from oteapi.models import ResourceConfig, SessionUpdate
from pydantic import ConfigDict, Field

from oteapi_optimade.models.config import OPTIMADEConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl


class OPTIMADEResourceConfig(ResourceConfig):
    """OPTIMADE-specific resource strategy config."""

    accessUrl: Annotated[
        OPTIMADEUrl,
        Field(
            description="Either a base OPTIMADE URL or a full OPTIMADE URL.",
        ),
    ]
    accessService: Annotated[
        Literal[
            "optimade",
            "OPTIMADE",
            "OPTiMaDe",
            "optimade+dlite",
            "OPTIMADE+dlite",
            "OPTiMaDe+dlite",
            "optimade+DLite",
            "OPTIMADE+DLite",
            "OPTiMaDe+DLite",
        ],
        Field(
            description="The registered strategy name for OPTIMADEResourceStrategy.",
        ),
    ]
    configuration: Annotated[
        OPTIMADEConfig,
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = OPTIMADEConfig()


class OPTIMADEResourceSession(SessionUpdate):
    """OPTIMADE session for the resource strategy."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    optimade_config: Annotated[
        Optional[OPTIMADEConfig],
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = None
    optimade_resources: Annotated[
        List[Dict[str, Any]],
        Field(
            description=(
                "List of OPTIMADE resources (structures, references, errors, ...) returned"
                " from the OPTIMADE request."
            ),
        ),
    ] = []
    optimade_resource_model: Annotated[
        str,
        Field(
            description=(
                "Importable path to the resource model to be used to parse the OPTIMADE "
                "resources in `optimade_resource`. The importable path should be a fully "
                "importable path to a module separated by a colon (`:`) to then define the "
                "resource model class name. This means one can then do:\n\n```python\n"
                "from PACKAGE.MODULE import RESOURCE_CLS\n```\nFrom the value "
                "`PACKAGE.MODULE:RESOURCE_CLS`"
            ),
            pattern=(
                r"^([a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*"  # package.module
                r":[a-zA-Z][a-zA-Z0-9_]*)?$"  # class
            ),
        ),
    ] = ""

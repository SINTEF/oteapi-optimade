"""Models specific to the resource strategy."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from oteapi.models import AttrDict, ResourceConfig
from pydantic import BeforeValidator, ConfigDict, Field

from oteapi_optimade.models.config import OPTIMADEConfig, OPTIMADEDLiteConfig
from oteapi_optimade.models.custom_types import OPTIMADEUrl


class OPTIMADEResourceConfig(ResourceConfig):
    """OPTIMADE-specific resource strategy config."""

    resourceType: Annotated[
        # later OPTIMADE/references and more should be added and other resources
        Literal["optimade/structures"],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(description=ResourceConfig.model_fields["resourceType"].description),
    ]
    accessUrl: Annotated[
        OPTIMADEUrl,
        Field(description="Either a base OPTIMADE URL or a full OPTIMADE URL."),
    ]
    accessService: Annotated[
        Literal["optimade", "optimade+dlite"],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(
            description="The registered strategy name for OPTIMADEResourceStrategy.",
        ),
    ]
    configuration: Annotated[
        Union[OPTIMADEConfig | OPTIMADEDLiteConfig],
        Field(
            description=(
                "OPTIMADE configuration. Contains relevant information necessary to "
                "perform OPTIMADE queries."
            ),
        ),
    ] = OPTIMADEConfig()


class OPTIMADEResourceResult(AttrDict):
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
        list[dict[str, Any]],
        Field(
            description=(
                "List of OPTIMADE resources (structures, references, errors, ...) returned"
                " from the OPTIMADE request."
            ),
        ),
    ] = []  # noqa: RUF012
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

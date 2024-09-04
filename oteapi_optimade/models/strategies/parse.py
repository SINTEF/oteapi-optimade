"""Models specific to the parse strategy."""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal, Optional

from oteapi.models import AttrDict, ParserConfig
from pydantic import AnyHttpUrl, BeforeValidator, ConfigDict, Field, field_validator

from oteapi_optimade.models.config import OPTIMADEConfig, OPTIMADEDLiteConfig

SUPPORTED_ENTITIES = [
    re.compile(_)
    for _ in [
        r"http://onto-ns.com/meta/[0-9]+(\.[0-9]+)?(\.[0-9]+)?/OPTIMADEStructure",  # Default
        r"http://onto-ns\.com/meta/[0-9]+(\.[0-9]+)?(\.[0-9]+)?/OPTIMADEStructureResource",
    ]
]
"""Supported entities for the OPTIMADE parse strategy.

The default entity is "OPTIMADEStructure".
This means, if no entity is provided, the default entity will be used.
"""


class OPTIMADEParseConfig(ParserConfig):
    """OPTIMADE-specific parse strategy config."""

    parserType: Annotated[
        Literal["parser/optimade"],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(
            description=ParserConfig.model_fields["parserType"].description,
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

    @field_validator("entity", mode="after")
    def _validate_entity(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        """Validate entity."""
        test_value = str(value).rstrip("/")

        for entity_pattern in SUPPORTED_ENTITIES:
            if entity_pattern.fullmatch(test_value):
                return value

        raise ValueError(
            f"Unsupported entity: {value}. Supported entities: {SUPPORTED_ENTITIES}"
        )


class OPTIMADEParseResult(AttrDict):
    """OPTIMADE parse strategy result."""

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
    optimade_response_model: Annotated[
        Optional[tuple[str, str]],
        Field(
            description=(
                "An OPTIMADE Python tools (OPT) pydantic successful response model. "
                "More specifically, a tuple of the module and name of the pydantic "
                "model."
            ),
        ),
    ] = None
    optimade_response: Annotated[
        Optional[dict[str, Any]],
        Field(
            description="An OPTIMADE response as a Python dictionary.",
        ),
    ] = None


class OPTIMADEDLiteParseConfig(OPTIMADEParseConfig):
    """OPTIMADE-specific parse strategy config when using DLite."""

    parserType: Annotated[  # type: ignore[assignment]
        Literal["parser/optimade/dlite"],
        BeforeValidator(lambda x: x.lower() if isinstance(x, str) else x),
        Field(description=ParserConfig.model_fields["parserType"].description),
    ]

    configuration: Annotated[  # type: ignore[assignment]
        OPTIMADEDLiteConfig,
        Field(
            description=(
                "OPTIMADE configuration when using the DLite-specific strategies. "
                "Contains relevant information necessary to perform OPTIMADE queries."
            ),
        ),
    ] = OPTIMADEDLiteConfig()

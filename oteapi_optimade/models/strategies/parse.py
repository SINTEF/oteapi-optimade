"""Models specific to the parse strategy."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional

from oteapi.models import AttrDict, ParserConfig
from pydantic import AnyHttpUrl, ConfigDict, Field, field_validator

from oteapi_optimade.models.config import OPTIMADEConfig, OPTIMADEDLiteConfig


class OPTIMADEParseConfig(ParserConfig):
    """OPTIMADE-specific parse strategy config."""

    entity: Annotated[
        AnyHttpUrl,
        Field(description=ParserConfig.model_fields["entity"].description),
    ] = AnyHttpUrl("http://onto-ns.com/meta/1.0/OPTIMADEStructure")

    parserType: Annotated[
        Literal["parser/optimade", "parser/OPTIMADE", "parser/OPTiMaDe"],
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
        supported_entities = {"http://onto-ns.com/meta/1.0/OPTIMADEStructure"}
        if value not in (AnyHttpUrl(_) for _ in supported_entities):
            raise ValueError(
                f"Unsupported entity: {value}. Supported entities: {supported_entities}"
            )

        return value


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
        Literal[
            "parser/optimade/dlite",
            "parser/OPTIMADE/dlite",
            "parser/OPTiMaDe/dlite",
            "parser/optimade/DLite",
            "parser/OPTIMADE/DLite",
            "parser/OPTiMaDe/DLite",
        ],
        Field(
            description=ParserConfig.model_fields["parserType"].description,
        ),
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

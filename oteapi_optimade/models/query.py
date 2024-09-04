"""Data models related to OPTIMADE queries."""

from __future__ import annotations

import inspect
from typing import Annotated, Optional
from urllib.parse import quote, unquote, urlencode

from optimade.server.query_params import EntryListingQueryParams
from pydantic import BaseModel, EmailStr, Field
from pydantic.fields import FieldInfo

QUERY_PARAMETERS = {
    "annotations": {
        name: FieldInfo.from_annotation(parameter.annotation)
        for name, parameter in (
            inspect.signature(EntryListingQueryParams).parameters.items()
        )
    },
    "defaults": EntryListingQueryParams(),
}
"""Entry listing URL query parameters from the `optimade` package
([`EntryListingQueryParams`](https://www.optimade.org/optimade-python-tools/api_reference/server/query_params/#optimade.server.query_params.EntryListingQueryParams))."""


class OPTIMADEQueryParameters(BaseModel, validate_assignment=True):
    """Common OPTIMADE entry listing endpoint query parameters."""

    filter: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS["annotations"]["filter"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].filter or None
    )
    response_format: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS["annotations"]["response_format"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].response_format or None
    )
    email_address: Annotated[
        Optional[EmailStr],
        Field(
            description=QUERY_PARAMETERS["annotations"]["email_address"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].email_address or None
    )
    response_fields: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS["annotations"]["response_fields"].description,
            pattern=QUERY_PARAMETERS["annotations"]["response_fields"]
            .metadata[0]
            .pattern,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].response_fields or None
    )
    sort: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS["annotations"]["sort"].description,
            pattern=QUERY_PARAMETERS["annotations"]["sort"].metadata[0].pattern,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].sort or None
    )
    page_limit: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_limit"].description,
            ge=QUERY_PARAMETERS["annotations"]["page_limit"].metadata[0].ge,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_limit or None
    )
    page_offset: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_offset"].description,
            ge=QUERY_PARAMETERS["annotations"]["page_offset"].metadata[0].ge,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_offset or None
    )
    page_number: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_number"].description,
            # ge=QUERY_PARAMETERS["annotations"]["page_number"].metadata[0].ge,
            # This constraint is only 'RECOMMENDED' in the specification, so should not
            # be included here or in the OpenAPI schema.
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_number or None
    )
    page_cursor: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_cursor"].description,
            ge=QUERY_PARAMETERS["annotations"]["page_cursor"].metadata[0].ge,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_cursor or None
    )
    page_above: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_above"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_above or None
    )
    page_below: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS["annotations"]["page_below"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].page_below or None
    )
    include: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS["annotations"]["include"].description,
        ),
    ] = (
        QUERY_PARAMETERS["defaults"].include or None
    )
    # api_hint is not yet initialized in `EntryListingQueryParams`.
    # These values are copied verbatim from `optimade==0.16.10`.
    api_hint: Annotated[
        Optional[str],
        Field(
            description=(
                "If the client provides the parameter, the value SHOULD have the format "
                "`vMAJOR` or `vMAJOR.MINOR`, where MAJOR is a major version and MINOR is a"
                " minor version of the API. For example, if a client appends "
                "`api_hint=v1.0` to the query string, the hint provided is for major "
                "version 1 and minor version 0."
            ),
            pattern=r"(v[0-9]+(\.[0-9]+)?)?",
        ),
    ] = ""

    def generate_query_string(self) -> str:
        """Generate a valid URL query string based on the set fields."""
        res = {}
        for field, value in self.model_dump().items():
            if value or field in self.model_fields_set:
                res[field] = unquote(value) if isinstance(value, str) else value
        return urlencode(res, quote_via=quote)

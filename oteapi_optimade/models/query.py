"""Data models related to OPTIMADE queries."""
from typing import Optional, Annotated
from urllib.parse import quote, unquote, urlencode

from optimade.server.query_params import EntryListingQueryParams
from pydantic import BaseModel, EmailStr, Field

QUERY_PARAMETERS = EntryListingQueryParams()
"""Entry listing URL query parameters from the `optimade` package
([`EntryListingQueryParams`](https://www.optimade.org/optimade-python-tools/api_reference/server/query_params/#optimade.server.query_params.EntryListingQueryParams))."""


class OPTIMADEQueryParameters(BaseModel, validate_assignment=True):
    """Common OPTIMADE entry listing endpoint query parameters."""

    filter: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS.filter.description,
        ),
    ] = QUERY_PARAMETERS.filter.default
    response_format: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS.response_format.description,
        ),
    ] = QUERY_PARAMETERS.response_format.default
    email_address: Annotated[
        Optional[EmailStr],
        Field(
            description=QUERY_PARAMETERS.email_address.description,
        ),
    ] = QUERY_PARAMETERS.email_address.default
    response_fields: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS.response_fields.description,
            pattern=QUERY_PARAMETERS.response_fields.pattern,
        ),
    ] = QUERY_PARAMETERS.response_fields.default
    sort: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS.sort.description,
            pattern=QUERY_PARAMETERS.sort.pattern,
        ),
    ] = QUERY_PARAMETERS.sort.default
    page_limit: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_limit.description,
            ge=QUERY_PARAMETERS.page_limit.ge,
        ),
    ] = QUERY_PARAMETERS.page_limit.default
    page_offset: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_offset.description,
            ge=QUERY_PARAMETERS.page_offset.ge,
        ),
    ] = QUERY_PARAMETERS.page_offset.default
    page_number: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_number.description,
            ge=QUERY_PARAMETERS.page_number.ge,
        ),
    ] = QUERY_PARAMETERS.page_number.default
    page_cursor: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_cursor.description,
            ge=QUERY_PARAMETERS.page_cursor.ge,
        ),
    ] = QUERY_PARAMETERS.page_cursor.default
    page_above: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_above.description,
            ge=QUERY_PARAMETERS.page_above.ge,
        ),
    ] = QUERY_PARAMETERS.page_above.default
    page_below: Annotated[
        Optional[int],
        Field(
            description=QUERY_PARAMETERS.page_below.description,
            ge=QUERY_PARAMETERS.page_below.ge,
        ),
    ] = QUERY_PARAMETERS.page_below.default
    include: Annotated[
        Optional[str],
        Field(
            description=QUERY_PARAMETERS.include.description,
        ),
    ] = QUERY_PARAMETERS.include.default
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

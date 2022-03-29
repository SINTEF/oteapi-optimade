"""Data models related to OPTIMADE queries."""
from typing import Optional
from urllib.parse import quote, unquote, urlencode

from optimade.server.query_params import EntryListingQueryParams
from pydantic import BaseModel, EmailStr, Field

QUERY_PARAMETERS = EntryListingQueryParams()
"""Entry listing URL query parameters from the `optimade` package
([`EntryListingQueryParams`](https://www.optimade.org/optimade-python-tools/api_reference/server/query_params/#optimade.server.query_params.EntryListingQueryParams))."""  # pylint: disable=line-too-long


class OPTIMADEQueryParameters(BaseModel, validate_assignment=True):
    """Common OPTIMADE entry listing endpoint query parameters."""

    filter: Optional[str] = Field(
        QUERY_PARAMETERS.filter.default,
        description=QUERY_PARAMETERS.filter.description,
    )
    response_format: Optional[str] = Field(
        QUERY_PARAMETERS.response_format.default,
        description=QUERY_PARAMETERS.response_format.description,
    )
    email_address: Optional[EmailStr] = Field(
        QUERY_PARAMETERS.email_address.default,
        description=QUERY_PARAMETERS.email_address.description,
    )
    response_fields: Optional[str] = Field(
        QUERY_PARAMETERS.response_fields.default,
        description=QUERY_PARAMETERS.response_fields.description,
        regex=QUERY_PARAMETERS.response_fields.regex,
    )
    sort: Optional[str] = Field(
        QUERY_PARAMETERS.sort.default,
        description=QUERY_PARAMETERS.sort.description,
        regex=QUERY_PARAMETERS.sort.regex,
    )
    page_limit: Optional[int] = Field(
        QUERY_PARAMETERS.page_limit.default,
        description=QUERY_PARAMETERS.page_limit.description,
        ge=QUERY_PARAMETERS.page_limit.ge,
    )
    page_offset: Optional[int] = Field(
        QUERY_PARAMETERS.page_offset.default,
        description=QUERY_PARAMETERS.page_offset.description,
        ge=QUERY_PARAMETERS.page_offset.ge,
    )
    page_number: Optional[int] = Field(
        QUERY_PARAMETERS.page_number.default,
        description=QUERY_PARAMETERS.page_number.description,
        ge=QUERY_PARAMETERS.page_number.ge,
    )
    page_cursor: Optional[int] = Field(
        QUERY_PARAMETERS.page_cursor.default,
        description=QUERY_PARAMETERS.page_cursor.description,
        ge=QUERY_PARAMETERS.page_cursor.ge,
    )
    page_above: Optional[int] = Field(
        QUERY_PARAMETERS.page_above.default,
        description=QUERY_PARAMETERS.page_above.description,
        ge=QUERY_PARAMETERS.page_above.ge,
    )
    page_below: Optional[int] = Field(
        QUERY_PARAMETERS.page_below.default,
        description=QUERY_PARAMETERS.page_below.description,
        ge=QUERY_PARAMETERS.page_below.ge,
    )
    include: Optional[str] = Field(
        QUERY_PARAMETERS.include.default,
        description=QUERY_PARAMETERS.include.description,
    )
    # api_hint is not yet initialized in `EntryListingQueryParams`.
    # These values are copied verbatim from `optimade==0.16.10`.
    api_hint: Optional[str] = Field(
        "",
        description=(
            "If the client provides the parameter, the value SHOULD have the format "
            "`vMAJOR` or `vMAJOR.MINOR`, where MAJOR is a major version and MINOR is a"
            " minor version of the API. For example, if a client appends "
            "`api_hint=v1.0` to the query string, the hint provided is for major "
            "version 1 and minor version 0."
        ),
        regex=r"(v[0-9]+(\.[0-9]+)?)?",
    )

    def generate_query_string(self) -> str:
        """Generate a valid URL query string based on the set fields."""
        res = {}
        for field, value in self.dict().items():
            if (
                value
                or field
                in self.__fields_set__  # pylint: disable=unsupported-membership-test
            ):
                res[field] = unquote(value) if isinstance(value, str) else value
        return urlencode(res, quote_via=quote)

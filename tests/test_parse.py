"""Test parse strategies."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oteapi.interfaces import IParseStrategy

    from oteapi_optimade.strategies.parse import SessionUpdateJSONParse


def test_json() -> None:
    """Test `application/jsonDEMO` demo parse strategy."""
    from oteapi_optimade.strategies.parse import DemoJSONDataParseStrategy

    data = {
        "firstName": "Joe",
        "lastName": "Jackson",
        "gender": "male",
        "age": 28,
        "address": {"streetAddress": "101", "city": "San Diego", "state": "CA"},
        "phoneNumbers": [{"type": "home", "number": "7349282382"}],
    }

    config = {
        "downloadUrl": "https://filesamples.com/samples/code/json/sample2.json",
        "mediaType": "application/jsonDEMO",
    }
    parser: "IParseStrategy" = DemoJSONDataParseStrategy(config)
    parsed_data: "SessionUpdateJSONParse" = parser.get()

    assert parsed_data.content == data

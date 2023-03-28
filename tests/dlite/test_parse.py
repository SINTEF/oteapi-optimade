"""Test `oteapi_optimade.dlite.parse` module."""
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("return_object", [True, False])
def test_parse(static_files: "Path", return_object: bool) -> None:
    """Test parsing."""
    import json

    from oteapi.datacache import DataCache
    from oteapi_dlite.utils import get_collection

    from oteapi_optimade.dlite.parse import OPTIMADEDLiteParseStrategy
    from oteapi_optimade.models import OPTIMADEDLiteParseConfig
    from oteapi_optimade.models.custom_types import OPTIMADEUrl

    url = OPTIMADEUrl(
        "https://example.org/some/base/v0.1/optimade/v1/structures"
        '?filter=elements HAS ALL "Si","O"&sort=nelements&page_limit=2'
    )
    config = OPTIMADEDLiteParseConfig(
        **{
            "mediaType": "application/vnd.OPTIMADE+DLite",
            "downloadUrl": url,
            "configuration": {
                "datacache_config": {
                    "expireTime": 60 * 60 * 24,
                    "tag": "optimade",
                    "accessKey": url,
                },
                "return_object": return_object,
            },
        }
    )

    cache = DataCache(config.configuration.datacache_config)
    sample_file = static_files / "optimade_response.json"
    cache.add(
        {
            "status_code": 200,
            "ok": True,
            "json": json.loads(sample_file.read_bytes()),
        }
    )

    session = OPTIMADEDLiteParseStrategy(config).initialize({})
    session = OPTIMADEDLiteParseStrategy(config).get(session)

    dlite_collection = get_collection(session)
    assert dlite_collection
    print(dlite_collection)

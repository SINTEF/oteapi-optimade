#!/usr/bin/env python3
"""End-to-end testing in CI for OTEAPI OPTIMADE (using OTELib)."""
from __future__ import annotations

import importlib
import json
import os
import sys


def _check_import(package_: str) -> str:
    """Utility function to check a relevant Python package exists."""
    try:
        importlib.import_module(package_)
    except ImportError:
        return (
            f"{package_} not found on the system!\n"
            f"Please install {package_} by running:\n\n"
            f"    pip install {package_}\n\n"
        )

    return ""


def _check_service_availability(service_url: str) -> None:
    """Utility function to check availability of a web service.

    Note, this expects the service is created using FastAPI.
    Or that at least a reachable `/docs` endpoint exists.
    """
    import requests

    error_message = f"Cannot connect to {service_url} !"

    try:
        response = requests.get(f"{service_url}/docs", allow_redirects=True, timeout=30)
    except (requests.ConnectionError, requests.ConnectTimeout) as exc_:
        raise RuntimeError(error_message) from exc_

    if not response.ok:
        raise RuntimeError(error_message)


def main(oteapi_url: str) -> None:
    """The main test function.

    The test information is taken from here:
    https://github.com/Materials-Consortia/optimade-python-tools/blob/master/tests/server/query_params/test_filter.py#L52
    and here:
    https://github.com/Materials-Consortia/optimade-python-tools/blob/master/tests/server/query_params/test_filter.py#L391

    """
    from optimade.adapters import Structure
    from otelib import OTEClient
    from pydantic import ValidationError

    from oteapi_optimade.models import OPTIMADEResourceResult

    client = OTEClient(oteapi_url)

    config = {
        "query_parameters": {
            "filter": 'elements HAS "Ac"',
            "page_limit": 2,
        }
    }

    source = client.create_dataresource(
        resourceType="OPTIMADE/structures",
        accessService="OPTIMADE",
        accessUrl=OPTIMADE_URL,
        configuration=config,
    )

    output = source.get()

    error_message = "Could not parse returned session as an OPTIMADEResourceStrategy."

    try:
        output = OPTIMADEResourceResult(**json.loads(output))
    except ValidationError as exc_:
        raise RuntimeError(error_message) from exc_

    assert output.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert len(output.optimade_resources) == 2

    for resource in tuple(output.optimade_resources):
        parsed_resource = Structure(resource)
        assert parsed_resource.id in ["mpf_1", "mpf_110"]

    # Use a filter strategy
    query = client.create_filter(
        filterType="OPTIMADE",
        query='NOT( elements HAS "Ag" AND nelements>1 )',
        limit=4,
        configuration=config,
    )

    pipeline = query >> source
    output = pipeline.get()

    try:
        # Should be an OPTIMADEResourceResult because `source` is last in the pipeline
        output = OPTIMADEResourceResult(**json.loads(output))
    except ValidationError as exc_:
        raise RuntimeError(error_message) from exc_

    assert output.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert len(output.optimade_resources) == 4

    for resource in tuple(output.optimade_resources):
        parsed_resource = Structure(resource)
        assert parsed_resource.id in [
            "mpf_1",
            "mpf_23",
            "mpf_30",
            "mpf_110",
            "mpf_3803",
            "mpf_3819",
            "mpf_200",
        ]


if __name__ == "__main__":
    # Check Python packages
    NECESSARY_PACKAGES = "otelib", "oteapi_optimade", "requests", "optimade"
    MESSAGES = ""
    for package in NECESSARY_PACKAGES:
        MESSAGES += _check_import(package)
    if MESSAGES:
        raise ImportError(MESSAGES)

    # Configuration
    PORT = os.getenv("OTEAPI_PORT", "8080")
    OTEAPI_SERVICE_URL = f"http://localhost:{PORT}"
    OTEAPI_PREFIX = os.getenv("OTEAPI_PREFIX", "/api/v1")
    OPTIMADE_URL = f"http://{os.getenv('OPTIMADE_HOST', 'localhost')}:{os.getenv('OPTIMADE_PORT', '5000')}/"
    if "OTEAPI_PREFIX" not in os.environ:
        # Set environment variables
        os.environ["OTEAPI_PREFIX"] = OTEAPI_PREFIX

    try:
        _check_service_availability(service_url=OTEAPI_SERVICE_URL)
    except RuntimeError as exc:
        sys.exit(str(exc))

    try:
        main(oteapi_url=OTEAPI_SERVICE_URL)
    except Exception as exc:
        sys.exit(str(exc))

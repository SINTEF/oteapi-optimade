#!/usr/bin/env python3
"""End-to-end testing in CI for OTEAPI OPTIMADE (using OTELib)."""
# pylint: disable=import-outside-toplevel
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
    else:
        return ""


def _check_service_availability(service_url: str) -> None:
    """Utility function to check availability of a web service.

    Note, this expects the service is created using FastAPI.
    Or that at least a reachable `/docs` endpoint exists.
    """
    import requests

    try:
        response = requests.get(f"{service_url}/docs", allow_redirects=True)
    except (requests.ConnectionError, requests.ConnectTimeout) as exc_:
        raise RuntimeError(f"Cannot connect to {service_url} !") from exc_
    else:
        if not response.ok:
            raise RuntimeError(f"Cannot connect to {service_url} !")


def main(oteapi_url: str) -> None:
    """The main test function.

    The test information is taken from here:
    https://github.com/Materials-Consortia/optimade-python-tools/blob/master/tests/server/query_params/test_filter.py#L52

    """
    from optimade.adapters import Structure
    from otelib import OTEClient
    from pydantic import ValidationError

    from oteapi_optimade.models import OPTIMADEResourceSession

    client = OTEClient(oteapi_url)

    config = {
        "query_parameters": {
            "filter": 'elements HAS "Ac"',
            "page_limit": 2,
        }
    }

    source = client.create_dataresource(
        accessService="OPTIMADE",
        accessUrl="http://optimade:5000/structures",
        configuration=config,
    )

    session = source.get()

    try:
        session = OPTIMADEResourceSession(**json.loads(session))
    except ValidationError as exc_:
        raise RuntimeError(
            "Could not parse returned session as an OPTIMADEResourceStrategy."
        ) from exc_

    assert session.optimade_resource_model == f"{Structure.__module__}:Structure"
    assert len(session.optimade_resources) == 2

    results = []
    for resource in tuple(session.optimade_resources):
        results.append(Structure(resource))
        assert results[-1].id in ["mpf_1", "mpf_110"]


if __name__ == "__main__":
    # Check Python packages
    NECESSARY_PACKAGES = "otelib", "oteapi_optimade", "requests", "optimade"
    MESSAGES = ""
    for package in NECESSARY_PACKAGES:
        MESSAGES += _check_import(package)
    if MESSAGES:
        raise ImportError(MESSAGES)

    # Configuration
    PORT = os.getenv("PORT", "8080")
    OTEAPI_SERVICE_URL = f"http://localhost:{PORT}"
    OTEAPI_PREFIX = os.getenv("OTEAPI_prefix", "/api/v1")
    if "OTEAPI_prefix" not in os.environ:
        # Set environment variables
        os.environ["OTEAPI_prefix"] = OTEAPI_PREFIX

    try:
        _check_service_availability(service_url=OTEAPI_SERVICE_URL)
    except RuntimeError as exc:
        sys.exit(exc)

    try:
        main(oteapi_url=OTEAPI_SERVICE_URL)
    except Exception as exc:  # pylint: disable=broad-except
        sys.exit(exc)

"""OTE-API OPTIMADE

A plugin for OTE-API.

Authored by Casper Welzel Andersen, SINTEF, 2022
Created from cookiecutter-oteapi-plugin, SINTEF, 2022
"""

from __future__ import annotations

import logging

__version__ = "0.5.0"
__author__ = "Casper Welzel Andersen"
__author_email__ = "casper.w.andersen@sintef.no"

logging.getLogger("oteapi_optimade").setLevel(logging.DEBUG)

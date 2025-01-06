"""OTE-API OPTIMADE

A plugin for OTE-API.

Authored by Casper Welzel Andersen, SINTEF, 2022
Created from cookiecutter-oteapi-plugin, SINTEF, 2022
"""

from __future__ import annotations

import logging

from ._utils import parse_assemblies, parse_species

__version__ = "0.6.0.dev0"
__author__ = "Casper Welzel Andersen"
__author_email__ = "casper.w.andersen@sintef.no"

logging.getLogger("oteapi_optimade").setLevel(logging.DEBUG)

__all__ = ("parse_assemblies", "parse_species")

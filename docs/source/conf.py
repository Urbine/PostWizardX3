# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "webmaster-seo-tools"
copyright = "2024, Yoham Gabriel (Urbine@GitHub)"
author = "Yoham Gabriel (Urbine@GitHub)"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

autodoc_type_aliases = {"List": "List", "Dict": "Dict"}

# typehints_use_signature = False
# simplify_optional_unions = True
# autodoc_preserve_defaults = False
# typehints_defaults = "comma"
typehints_use_rtype = False
typehints_fully_qualified = True

# In conf.py

# Napoleon settings
# Exclude `__init__` docstrings by default
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False  # Exclude private members by default
napoleon_use_param = True  # Use `:param` for parameters
napoleon_use_rtype = True  # Use `:rtype` for return types

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": False,
    "titles_only": False,
}

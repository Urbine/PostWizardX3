# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'webmaster-seo-tools'
copyright = '2024, Yoham Gabriel (Urbine@GitHub)'
author = 'Yoham Gabriel (Urbine@GitHub)'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # For automatic documentation from docstrings
    'sphinx.ext.viewcode',     # Adds links to highlighted source code
    'sphinx.ext.napoleon',
    'recommonmark'
]

# In conf.py

# Napoleon settings
napoleon_include_init_with_doc = False  # Exclude `__init__` docstrings by default
napoleon_include_private_with_doc = False  # Exclude private members by default
napoleon_use_param = True         # Use `:param` for parameters
napoleon_use_rtype = True         # Use `:rtype` for return types

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

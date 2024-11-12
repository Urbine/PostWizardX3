#!/bin/sh

# Fetch docs from project docstrings
sphinx-apidoc -o ./source ..
# Clean previous build files...
make clean
# Generate the new docs page...
make html
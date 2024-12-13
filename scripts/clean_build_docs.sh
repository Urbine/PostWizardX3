#!/bin/sh

# Go to ``docs`` to find the /source directory
cd ~/GitHub/webmaster-seo-tools/docs

# Fetch docs from project docstrings
sphinx-apidoc -o ./source ..

# Clean previous build files...
make clean

# Generate the new docs page...
make html
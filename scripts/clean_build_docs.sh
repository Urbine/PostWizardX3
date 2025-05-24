#!/bin/sh

set -euo pipefail

# Go to ``docs`` to find the /source directory

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the directory containing the 'source' directory as an argument for this script."
  exit
fi

# Fetch docs from project docstrings
sphinx-apidoc -o ./source ..

# Clean previous build files...
make clean

# Generate the new docs page...
make html
#!/bin/sh
set -euo pipefail

if [ "$1" != "" ]; then
  dir="$1"
else
  dir='.'
fi

find "$dir" -name "*.py" -not -path "./.venv/*" | xargs ruff format
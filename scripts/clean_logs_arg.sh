#!/bin/sh
set -euo pipefail
# Cleans outdated files with list of space-separated hints.
# Optional parameter --invert passed in as argument to clean today's logs.
python3 -m tasks.clean_outdated_files --folder './logs' --ext '.log' --hints log "$1"

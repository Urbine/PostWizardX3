#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" = "" ]; then
  echo "Please provide the directory you need cleaned as an argument for this script."
  exit
fi

# Cleans outdated files with list of space-separated hints.
python3 -m workflows.tasks.clean_outdated_files --folder "$targetdir" --ext '.db' --hints trike asian euro tuktuk abjav wp vjav desi fap

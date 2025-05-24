#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the root directory of the project as an argument for this script."
  exit
fi

echo "--> Testing function clean_filename from the core package:"
python3 -m unittest ./tests/test_clean_filename.py

echo "--> Testing function is_parent_dir_required from the core package:"
python3 -m unittest ./tests/test_is_parent_dir_required.py

echo "--> Testing function parse_date_to_iso from the core package:"
python3 -m unittest ./tests/test_parse_date_to_iso.py

echo "--> Testing function clean_partner_tag from the workflows package:"
python3 -m unittest ./tests/test_clean_partner_tag.py

echo "--> Testing function make_slug from the workflows package:"
python3 -m unittest ./tests/test_make_slug.py
#!/bin/sh

# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

venv=$(pwd | grep -c venv)
if [ "$venv" = 1 ];then
  # Go to parent dir if executed from .venv
  cd ..
else
  :
fi

echo "--> Testing function clean_filename from the core package:"
python3 -m unittest ./tests/test_clean_filename.py

echo "--> Testing function is_parent_dir_required from the core package:"
python3 -m unittest ./tests/test_is_parent_dir_required.py

echo "--> Testing function parse_date_to_iso from the core package:"
python3 -m unittest ./tests/test_parse_date_to_iso.py

echo "--> Testing function clean_partner_tag from the workflows package:"
python3 -m unittest ./tests/test_clean_partner_tag.py
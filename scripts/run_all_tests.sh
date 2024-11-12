#!/bin/sh

# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

echo "--> Testing function clean_filename from the common package:"
python3 -m unittest ./tests/test_clean_filename.py

echo "--> Testing function is_parent_dir_required from the common package:"
python3 -m unittest ./tests/test_is_parent_dir_required.py

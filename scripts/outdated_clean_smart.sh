#!/bin/sh

# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

# Cleans outdated files with list of space-separated hints.
python3 -m workflows.clean_outdated_files --folder '.' --ext '.db' --hints trike asian euro tuktuk abjav
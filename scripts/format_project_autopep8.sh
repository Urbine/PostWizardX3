#!/bin/sh

# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
else
  :
fi

find -name "*.py" | xargs autopep8 --in-place --aggressive

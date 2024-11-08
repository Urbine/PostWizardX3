#!/bin/sh

curr_dir=$(pwd | cut -d'/' -f6)
if [ "$curr_dir" = "scripts" ];then
   cd ..
else
  :
fi

python3 -m workflows.clean_outdated_files --folder '.' --ext '.db' --hints partner_c partnerone partnerfour partnertwo partnerseven
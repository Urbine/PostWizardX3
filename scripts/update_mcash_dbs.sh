#!/bin/sh

# In case there is a dir change this variable will be set to one.
cd_init=0
# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" != 1 ];then
   # Go to parent dir
   cd ~/GitHub/webmaster-seo-tools
   cd_init=1
else
  :
fi

echo "** Updating TukTuk Patrol Database... **"
python3 -m workflows.update_mcash_chain ./tmp --hint tuktuk --gecko --headless
echo -e "\n"
echo "** Updating ASD Database... **"
python3 -m workflows.update_mcash_chain ./tmp --hint asian --gecko --headless
echo -e "\n"
echo "** Updating Trike Patrol Database... **"
python3 -m workflows.update_mcash_chain ./tmp --hint asian --gecko --headless
echo -e "\n"
echo "** Cleaning old databases... **"
if [ "$cd_init" = 1 ];then
  # if the script moved to the parent dir, it has to come back
  ./scripts/outdated_clean_smart.sh
else
  ./outdated_clean_smart.sh
fi
# Back to the starting directory
cd -
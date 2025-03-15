#!/bin/sh

# In case there is a dir change this variable will be set to one.
cd_init=0
# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" != 1 ];then
   # Go to scripts dir if executed outside the scripts dir
   cd ~/GitHub/webmaster-seo-tools
   cd_init=1
else
  :
fi

echo "** Updating Tube Corporate Feeds databases... **"
# Defaults are: no more than 100 video entries sorted by popularity in the last 7 days
python3 -m integrations.tube_corp_feeds -days 7 -sort popularity -limit 100
echo -e "\n"
echo "** Updating AdultNext's Abjav database... **"
# 30 days for the AdultNext API integration
python3 -m integrations.adult_next_api -days 30 -sort popularity -limit 100
echo -e "\n"
echo "** Updating FapHouse databse... **"
python3 -m integrations.fhouse_api --no-embed-dur
echo "** Cleaning old databases... **"

if [ "$cd_init" = 1 ];then
  # if the script moved to the parent dir, it has to come back
  ./scripts/outdated_clean_smart.sh
else
  ./outdated_clean_smart.sh
fi
# Back to the starting directory
cd -

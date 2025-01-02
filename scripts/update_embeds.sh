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

echo "** Updating Feed Beta Feeds databases... **"
# Defaults are: no more than 100 video entries sorted by popularity in the last 7 days
python3 -m integrations.feed_beta_api -days 7 -sort popularity -limit 100
echo -e "\n"
echo "** Updating FeedAlpha database... **"
# 30 days for the FeedAlpha API integration
python3 -m integrations.feed_alpha_api -days 30 -sort popularity -limit 100
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
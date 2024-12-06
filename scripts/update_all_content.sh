#!/bin/sh
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" != 1 ];then
   # Go to scripts dir if executed outside the scripts dir
   cd ~/GitHub/webmaster-seo-tools/scripts
else
  :
fi

./update_embeds.sh
echo -e "\n"
./update_mcash_dbs.sh
# Back to the starting directory
cd -
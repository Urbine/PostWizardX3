#!/bin/sh

# In case there is a dir change this variable will be set to one.
cd_init=0
# Checks whether this script is running in the project's scripts dir.
curr_dir=$(pwd | grep -c scripts)
if [ "$curr_dir" = 1 ];then
   # Go to parent dir
   cd ..
   cd_init=1
else
  :
fi

echo "Fetching all posts information from WP..."
# Hard update of the wp_posts.json file with Yoast mode enabled
python3 -m integrations.wordpress_api --yoast
echo -e "\n"
# Hard update of the wp_photos.json file with Yoast mode enabled
echo "Fetching all photo posts information from WP..."
python3 -m integrations.wordpress_api --yoast --photos
echo -e "\n"
echo "Cleaning old databases..."
if [ "$cd_init" = 1 ];then
  # if the script moved to the parent dir, it has to come back
  ./scripts/outdated_clean_smart.sh
else if [ "$curr_dir" = 1 ];then
  ./outdated_clean_smart.sh
else
  ~/GitHub/webmaster-seo-tools/scripts/outdated_clean_smart.sh
fi

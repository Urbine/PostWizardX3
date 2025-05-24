#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the root directory of your project or where you want to output these resulting files as an argument for this script."
  exit
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

./scripts/outdated_clean_smart.sh


#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the root directory of your project or where you want to output the resulting files as an argument for this script."
  exit
fi

echo "** Updating Feed Beta Feeds databases... **"
# Defaults are: no more than 100 video entries sorted by popularity in the last 7 days
python3 -m integrations.feed_beta_api -days 7 -sort popularity -limit 100
echo -e "\n"
echo "** Updating FeedAlpha database... **"
# 30 days for the FeedAlpha API integration
python3 -m integrations.feed_alpha_api -days 30 -sort popularity -limit 100
echo -e "\n"
echo "** Updating FeedDelta database... **"
python3 -m integrations.feed_delta_api --no-embed-dur
echo "** Cleaning old databases... **"

./scripts/outdated_clean_smart.sh "$targetdir"

cd - || exit

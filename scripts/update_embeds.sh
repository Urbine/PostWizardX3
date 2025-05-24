#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the root directory of your project or where you want to output the resulting files as an argument for this script."
  exit
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

./scripts/outdated_clean_smart.sh "$targetdir"

cd - || exit

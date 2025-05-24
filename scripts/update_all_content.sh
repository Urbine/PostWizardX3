#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  echo "Please provide the root directory of your project or where you want to output the resulting files as an argument for this script."
  exit
fi

./update_embeds.sh  "$targetdir"
echo -e "\n"
/update_mcash_dbs.sh "$targetdir"
# Back to the starting directory
cd - || exit
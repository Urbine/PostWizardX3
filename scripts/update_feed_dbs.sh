#!/bin/sh
set -euo pipefail

targetdir="$1"
if [ "$targetdir" != "" ]; then
  cd "$targetdir"
else
  targetdir="."
fi

echo "** Updating PartnerTwo Database... **"
python3 -m workflows.update_media_source_chain --hint partnertwo --gecko --headless
echo -e "\n"
echo "** Updating ASD Database... **"
python3 -m workflows.update_media_source_chain --hint partnerone --gecko --headless
echo -e "\n"
echo "** Updating PartnerThree Database... **"
python3 -m workflows.update_media_source_chain --hint partner_c --gecko --headless
echo -e "\n"
echo "** Cleaning old databases... **"
./scripts/outdated_clean_smart.sh "$targetdir"
cd - || exit

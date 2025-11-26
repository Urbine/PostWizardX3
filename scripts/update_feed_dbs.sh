#!/bin/sh
set -euo pipefail

python3 -m flows.feed_updater --hint partnerone partnertwo partner_c --gecko --headless
echo -e "\n"
echo "** Cleaning old databases... **"
./scripts/outdated_clean_smart.sh "./artifacts"
cd - || exit

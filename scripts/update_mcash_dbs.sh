#!/bin/sh
set -euo pipefail

python3 -m flows.mcash_updater --hint asian tuktuk trike --gecko --headless
echo -e "\n"
echo "** Cleaning old databases... **"
./scripts/outdated_clean_smart.sh "./artifacts"
cd - || exit

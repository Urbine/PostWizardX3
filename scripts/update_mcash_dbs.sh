#!/bin/sh
set -euo pipefail

echo "** Updating TukTuk Patrol Database... **"
python3 -m workflows.update_mcash_chain --hint tuktuk --gecko --headless
echo -e "\n"
echo "** Updating ASD Database... **"
python3 -m workflows.update_mcash_chain --hint asian --gecko --headless
echo -e "\n"
echo "** Updating Trike Patrol Database... **"
python3 -m workflows.update_mcash_chain --hint trike --gecko --headless
echo -e "\n"
echo "** Cleaning old databases... **"
./scripts/outdated_clean_smart.sh "./artifacts"
cd - || exit

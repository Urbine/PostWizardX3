#!/bin/sh
set -euo pipefail

# Activate the Python virtual environment
source ./.venv/bin/activate
./scripts/update_embeds.sh
echo -e "\n"
./scripts/update_mcash_dbs.sh
#Deactivate the Python virtual environment
deactivate

# Back to the starting directory
cd - || exit
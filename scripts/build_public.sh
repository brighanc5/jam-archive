#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Verified production origin. Override when migrating to a custom domain.
export JAM_ARCHIVE_ORIGIN="${JAM_ARCHIVE_ORIGIN:-https://odd-king-7e31.brighamhancock.workers.dev}"
python3 build_v061.py
python3 validate.py
python3 -m unittest discover -s tests -v
node --check site/assets/discovery.js
python3 scripts/check_public_site.py

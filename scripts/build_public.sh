#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export JAM_ARCHIVE_ORIGIN="${JAM_ARCHIVE_ORIGIN:-https://odd-king-7e31.brighamhancock.workers.dev}"
python3 scripts/doctor.py
python3 build_v011.py
python3 validate.py
python3 -m unittest discover -s tests -v
node --check site/assets/discovery.js
node --check site/assets/recordings.js
node --check site/assets/time-machine.js
node --check site/assets/song-paths.js
node --check site/assets/connections.js
node --check site/assets/deep-archive.js
python3 scripts/safety_check.py
python3 scripts/check_public_site.py
printf '\nTHE JAM ARCHIVE v0.11 DEEP ARCHIVE FULL REPOSITORY BUILD: PASS\n'

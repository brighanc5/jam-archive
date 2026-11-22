#!/usr/bin/env bash
# Build the whole site and serve it at http://localhost:8000
#   bash scripts/dev.sh          full build + all checks, then serve
#   bash scripts/dev.sh --quick  skip the checks (about 2x faster), then serve
set -euo pipefail
cd "$(dirname "$0")/.."
export JAM_ARCHIVE_ORIGIN="${JAM_ARCHIVE_ORIGIN:-https://thejamarchive.org}"
if [[ "${1:-}" == "--quick" ]]; then
  python3 build_v014.py >/dev/null
  python3 scripts/polish_site.py >/dev/null
  python3 scripts/presentation_fixes.py
  python3 scripts/build_trails.py
  python3 scripts/build_upcoming.py
  python3 scripts/site_nav.py
  python3 scripts/house_style.py
else
  bash scripts/build_public.sh
fi
PORT="${PORT:-8000}"
echo "Serving site/ at http://localhost:$PORT  (Ctrl+C to stop)"
cd site && exec python3 -m http.server "$PORT"

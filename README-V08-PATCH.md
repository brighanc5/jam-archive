# The Jam Archive v0.8 — Time Machine (incremental patch)

This ZIP contains **only updated and newly added source files**, not a complete repository. It requires v0.7 and the overnight safety patch. **Do not overwrite the whole repository or discard existing files.**

## Install on Mac with GitHub Desktop

1. Open **GitHub Desktop**, choose the existing **jam-archive** repository, and select **Repository → Show in Finder**. This is the definitive working copy even if the directory is called `jam-archive-2`.
2. Extract this ZIP into a separate folder (Downloads is fine). Open the extracted folder. Its root has `history_seed.py`, `build_v08.py`, etc., plus `scripts/` and `tests/` subfolders.
3. Drag/copy its **contents** into the real GitHub repository folder, preserving the folder structure. Choose **Replace** for any matching source files. Do not create `jam-archive/jam-archive/...` or put the files inside `site/`. Keep unrelated files, including `data/approved_recordings.json`.
4. In Terminal, run `cd ` (with a trailing space), drag the real repository folder into Terminal, press Return. Then execute:

   ```bash
   bash scripts/build_public.sh
   ```

5. **Expected:** 27 tests pass, **284 sitemap URLs**, `PUBLIC CHECK PASS`, `OVERNIGHT SAFETY PASS`, and 25 historical shows / 17 recording references. If this command fails, **do not commit/push**; report the complete terminal error.
6. Optionally preview: `python3 -m http.server 8000 --directory site` and open `http://localhost:8000/time-machine/` in the browser. Control+C stops the server.
7. In GitHub Desktop, inspect **Changes**, commit as `Add v0.8 Time Machine historical collection`, and click **Push origin**. Wait for **GitHub Actions to pass** and check the Cloudflare deployment status. This ZIP has **not** modified GitHub or Cloudflare on its own.
8. After a successful deploy: https://odd-king-7e31.brighamhancock.workers.dev/time-machine/

## File paths from this patch

- `history_seed.py` — +16 verified concert listings, +8 official release pointers; no invented tapes.
- `build_v05.py` — handles shows with no known setlist, displays editor/source caveats; retains a required Python 3.11 compatibility fix for GitHub Actions.
- `build_v07.py` — corrects the approved-additions build metric once the seed catalog expands.
- `build_v08.py` — builds the interactive, source-backed static Time Machine and sitemap route.
- `time_machine.css`, `time_machine.js` — responsive timeline UI and progressive filters; no third-party scripts.
- `validate.py`, `scripts/check_public_site.py`, `scripts/build_public.sh` — updated counts, site checks, new build target and JS syntax check.
- `tests/test_time_machine.py` — 8 extra source, date, missing-evidence and site integration tests.
- `README.md`, `README-V08-PATCH.md`, `SOURCE_REVIEW_V08.md` — accurate documentation and audit notes.

## Scope / integrity

The new recording pointers are links to actual official commercial releases, **not** claims that downloads are free. The source pages and original recording custodians retain their rights. Historical setlist blanks stay blank; we do not backfill likely songs from other nights. Do not interpret the 1970 Atlanta Pop Festival's label date (July 5) or the Ludlow Garage recording date as settled where sources conflict.

The v0.8 static build performs **no internet requests** and adds no API subscriptions, cron schedules, hosted audio/video, user logins or databases. It has no way to verify your Cloudflare billing tier, live deployment status or actual legal permissions.

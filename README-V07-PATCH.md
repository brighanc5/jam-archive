# The Jam Archive v0.7 — Incremental source-only patch

**This ZIP is not a complete copy of your repository.** It deliberately omits the generated `site/`, databases, credentials, Git metadata and the existing v0.6.1 safety patch. It builds on a correctly applied v0.6.1 GitHub working copy.

## Apply with Finder and GitHub Desktop on macOS

1. In **GitHub Desktop**, select `jam-archive` under **Current Repository** and use **Repository → Show in Finder**. This opens the actual Git-connected folder, regardless of whether its name is `jam-archive` or `jam-archive-2`.
2. Extract `jam_archive_v07_RECORDING_EXPLORER_PATCH.zip` in Downloads. You will see folders `data/`, `scripts/` and `tests/`, alongside Python, JavaScript and CSS files.
3. **Merge their contents** into the *matching paths* of the Git-connected folder. Keep existing unrelated files. Overwrite files with matching names. Make sure `data/approved_recordings.json` is inside the repository's `data` directory; DO NOT copy a nested full `jam-archive` folder into your repository.
4. Open Terminal in that Git folder: type `cd ` (with a space), drag the repository folder from Finder into Terminal and hit Return.
5. Run `bash scripts/build_public.sh`. On success you will see **19 tests**, **246 sitemap URLs**, and **PUBLIC CHECK PASS**. If any error appears, do **not** push; paste the complete error into ChatGPT.
6. Optionally preview with `python3 -m http.server 8000 --directory site` and visit `http://localhost:8000/recordings/` on your Mac. Press Control+C to stop the preview server. (Opening the file directly through Finder will not load the JSON source index because browsers limit local-file fetches.)
7. In GitHub Desktop, inspect **Changes**, commit with message `Add v0.7 Recording Explorer and reviewed publication pipeline`, then **Push origin**. Your existing connected Cloudflare build should deploy after the push. Check GitHub Actions and Cloudflare for success before assuming it's live.
8. When deployed, visit `https://odd-king-7e31.brighamhancock.workers.dev/recordings/`.

## What this actually changes

- Adds a source-backed searchable and filterable **Recording Explorer** linking to existing curated performances. Initially **nine** existing sources—no new factual claims from live APIs.
- Adds `data/approved_recordings.json` as the Git-tracked publication ledger for new, manually checked recording links.
- Changes `build_v04.py` so **local research queue files cannot automatically become public recording links**. They remain pending research only.
- Adds `scripts/stage_approved.py`, a narrowly scoped local tool for staging already approved Internet Archive candidates attached to an existing curated show.
- Adds seven publication-integrity tests; total rises from 12 to 19.
- Preserves manual-only research, static Cloudflare hosting, and the existing overnight safety tripwire.

## What this does NOT change

- No automatic fetching on the live site, audio hosting, email alerts, user accounts, scheduled scraping, payment services, databases or paid Cloudflare bindings.
- No actual GitHub commit or live deployment has been executed by this patch.
- No new concerts, source recordings, or alleged musical facts have been added. Those need verified primary sources and reviewer approval.

## Why source data is still small

The explorer initially contains the nine carefully documented source references the archive already had. This milestone creates a maintainable ingestion/publishing route. Next: run a bounded approved-source research session, curate additional historical shows, and publish 10–25 defensible source pointers.

# The Jam Archive v0.11 — Deep Archive

Research edition: October 29, 2026. Complete repository replacement, not an incremental patch.

## New editorial material

- **22 researched dossiers:** 10 artists/musicians/projects and 12 existing concerts.
- **110 discrete source-linked assertions**, backed by 31 external bibliography records. Each claim identifies its source; bibliography exposes the publisher classification.
- **Open questions** per dossier. Contradictions are explicitly disclosed, notably the Atlanta Pop Festival billing-versus-clock-date and Ludlow Garage dating evidence.
- **Four new curated external recording references:** ABB March 12 early show (Fillmore box Disc 1), ABB June 27 (Eat a Peach Deluxe Edition), Grateful Dead May 7 Boston (Rhino boxed set), Phish August 22 Magnaball official links. New Recording Explorer total: 21.
- The **Deep Archive** directory is browseable without JavaScript; search and category filtering are optional enhancements.
- **Existing artist and concert pages** gain links and highlights only when an editorial dossier exists; the original 196 artist and 25 historical concert records are retained.
- All new pages have canonical URLs and sitemap entries. Build check counts all local hyperlinks and published files.

## Editorial boundaries

- Dated editorial review is **not** a claim of continuous URL uptime or automatic re-verification.
- A show is a performance; a recording is a source or release; a composition is not established by a same-title match.
- Commercial releases do not imply unrestricted audio copying or availability.
- Existing 25 show dossier records and 53 song-title records are deliberately preserved, not swollen with guessed setlists.
- A quoted or archived interview can substantiate an attributed account, not automatically prove the absolute truth of every recollection.
- We do not collect private user data, host recordings, or operate autonomous, scheduled publication.

## Limitations and next research priorities

The research coverage is **selected, not exhaustive**, especially for Goose, musician biographies, and unrecorded performances. Artist official sites can change over time. Future improvements should build typed personnel intervals, composition IDs, verified sit-in appearances, independent tape-lineage records, and per-show listening annotations from appropriately licensed sources.

## Verification

From the complete repository root:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
python3 scripts/check_live.py # after successful Cloudflare deployment only
```

Expected locally: **64 tests**, **309 sitemap routes**, **21 recording-source entries**, **110 research notes** and **OVERNIGHT SAFETY PASS**. Cloudflare must build source files using `bash scripts/build_public.sh`; `site/` is Git-ignored by design.

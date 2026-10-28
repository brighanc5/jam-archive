# The Jam Archive v0.9 — full-source recovery and Song Paths

Release date: October 28, 2026.

## Why a full repository instead of a patch?

Incremental ZIP copies can omit hidden `.github` directories or miss some files in `tests/`. This release restores the complete reproducible application source, test suite, workflows, and configuration. It does not contain a `.git` directory: retain the one inside your existing GitHub Desktop repository.

## New feature: Song Paths

- 53 indexed titles from 25 curated concert dossiers (20 have some known song excerpts).
- 106 appearances across those excerpts, cross-linked to source-backed shows and individual song pages.
- Search titles, documented venues/dates, filter performers and recurring titles, sort by frequency/title.
- Related songs are **co-indexed in the same selected show**; no implication of segues, solos, motifs, or complete setlists.
- All song cards and show links remain usable without JavaScript, using native disclosure elements.
- Public JSON export `site/assets/song-paths.json` supports future source-aware data exploration.

## Reliability and maintenance

- `python3 scripts/doctor.py` confirms correct release marker, complete source files, Git folder when available, Python/Node executables, and a full 37-case test suite.
- `scripts/build_public.sh` now invokes doctor first and builds the v0.9 layer after all previous layers.
- 10 new unit tests guard song counts, show links, cross-song claims, routes, assets, privacy exclusions, and sitemap.
- `scripts/check_public_site.py` validates the new route and song-paths JSON along with all previous links.
- GitHub validation still uses the same workflow and the same existing Worker ID, with no paid API calls or scheduled researcher.

## Acceptance results in the provided source build

- 37 unit tests passing.
- 285 sitemap URLs, 2,872 local HTML references checked.
- Safety preflight passing (code/config validation only, not a live billing audit).
- 196 artist/project pages; 25 curated shows; 17 reviewed recording references; 53 song pages; plus Recording Explorer, Time Machine and Song Paths.

## Not yet included

A live concert feed, verified modern-show import, user accounts, notifications, copyrighted concert audio, or a comprehensive setlist archive. Those require explicit later development and additional source verification.

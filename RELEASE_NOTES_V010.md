# The Jam Archive v0.10 — The Family Tree

Date: October 29, 2026.

## New experience: Six Degrees of Jam

- A responsive, interactive **Family Tree** page showing direct verified connections among musicians and projects.
- A **find-the-connection** feature calculates shortest pathways across the existing independently verified relationship records; every step provides a source link.
- Four source-backed sample paths featuring Trey/Les Claypool, Derek Trucks/Warren Haynes, Joe Russo/Leo Kottke, and Oteil Burbridge/John Mayer.
- A fully server-rendered relationship ledger, usable with JavaScript disabled; no framework/CDN dependencies.
- Every artist/project profile now links to the explorer. Unconnected entries are labeled as lacking an indexed verified relationship—not as lacking real-world connections.
- A public, compact JSON dataset at `/assets/connections.json` supports future evidence-based features.

**Scope and safeguards:** 52 previously verified relations, covering 55 graph nodes in 8 unconnected groups. Another 25 relationship leads explicitly marked `needs_review` remain excluded. Paths imply only a **chain of separately documented memberships/collaborations**. They do not establish guests, sit-ins, simultaneous lineups, influence, or encounters. No historical relationship facts were invented or scraped for this release.

## Reliability

- Fixed the Cloudflare custom 404 page's links and stylesheet to use absolute-root paths; previously nested missing routes created misleading links under the missing page path.
- Added a pre-build check for unresolved Git conflict markers, the source of the previous `build_v05.py` failure.
- Added `scripts/check_live.py` to distinguish a locally successful build from a Cloudflare deployment. The command is optional and read-only.
- 13 new provenance and publication tests; **50 passing tests** total.
- Full static build: **286 sitemap URLs** and **3,190 internal HTML links** checked.
- Existing no-licensed-media, manual-only research, reviewed publication, static-only Worker safety checks preserved.

## Still important

- The public graph is incomplete because the underlying source catalog is incomplete; no paths are inferred through the 25 unreviewed leads.
- Tour dates remain a dated, October 26, 2026 snapshot, not a live feed.
- Browser JavaScript syntax, static-route integrity and tests were checked locally; the site has not been independently verified on the user's live Cloudflare Worker from this development environment.
- Neither the original relationship sources nor their current reachability were re-validated by a fresh external crawl in this release; verification status is inherited from the curated source catalog.

Install using [INSTALL_V010_MAC.md](INSTALL_V010_MAC.md), not the earlier incremental patch instructions.

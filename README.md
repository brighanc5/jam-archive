# The Jam Archive

## v0.13 — Archive Atlas: major source-index expansion (October 29, 2026)

**Current complete-source release.** New [Archive Atlas](https://odd-king-7e31.brighamhancock.workers.dev/era-atlas/) indexes **361 distinct documented performance records** across the Allman Brothers, Grateful Dead, Phish and Goose. The site retains the 25 more deeply researched historical show dossiers and adds **336 date-and-venue index records**, 12 tour/history chapters, and 20 short source-attributed spotlights. Every new index-only page explicitly discloses that its source has **not** established a complete setlist, lineup, surviving recording or transfer lineage.

**91 tests, 672 sitemap routes, 673 generated HTML files and zero structural audit issues.** Source and scope metadata are tracked in `data/era_index.json` and published in a dedicated citation directory. The build remains offline, static, free of hosted recordings, and does not automatically publish research-agent discoveries.

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
python3 scripts/check_live.py  # After GitHub push and new Ready deployment only
```

Read [INSTALL_V013_MAC.md](INSTALL_V013_MAC.md), [RELEASE_NOTES_V013.md](RELEASE_NOTES_V013.md) and [ARCHIVE_ATLAS_EDITORIAL.md](ARCHIVE_ATLAS_EDITORIAL.md). Copy the *contents* of the full source directory into your actual GitHub Desktop working repository, **preserving `.git`**. This build has no remote side effects.

## v0.12 — Performance Lab + whole-site audit (October 29, 2026)

**Prior release.** New [Performance Lab](https://odd-king-7e31.brighamhancock.workers.dev/performance-lab/) documents 12 cited historic sequences, 62 individual track positions, 18 source-printed transition markers, and 2 song-specific guest credits. [Recording lineages](https://odd-king-7e31.brighamhancock.workers.dev/performance-lab/lineages/) distinguish the performance, tape source, transfer, mastering and commercial album where available. The study pages link back to their official or curated original sources; no concert audio is hosted.

The complete generated site now has **323 indexed routes, 79 unit tests and a 324-page structural audit**. Responsive section navigation, keyboard skip links, explicit labels and a dated/non-live tour snapshot improve usability and accuracy. **The local audit is not a live-hosted-site or browser visual audit.** Build and verify with:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
python3 scripts/check_live.py  # Only after successful Cloudflare deployment
```

Read **[INSTALL_V012_MAC.md](INSTALL_V012_MAC.md)**, **[RELEASE_NOTES_V012.md](RELEASE_NOTES_V012.md)** and **[AUDIT_REPORT_V012.md](AUDIT_REPORT_V012.md)**. This is a complete repository replacement: retain your existing `.git`, `.github` must be copied, and commit/push is required before Cloudflare updates.


## v0.11 — Deep Archive (research expansion)

Full replacement edition, source reviewed October 29, 2026.

- **New `/deep-archive/` directory**: 22 authored research dossiers, 110 linked assertions, 31 source references and open questions for each subject.
- **Four more approved external recording pointers**; 21 total recording references.
- Keeps all v0.10 musician connections, Time Machine, Song Paths and contribution/review safeguards.
- Uses `data/research_dossiers.json` as the permanent version-controlled editorial record, with no external service required at build time.
- Run `python3 scripts/doctor.py && bash scripts/build_public.sh`. For Mac installation, see **`INSTALL_V011_MAC.md`**.
- Read **`RELEASE_NOTES_V011.md`** for source-scope limitations and research priorities.


**Free · Fan-built · Source-first.** A public index of improvisational-music artists, performances, recordings and musical relationships. Historical and event data are incomplete research snapshots, not a live tour service.

**Live address:** https://odd-king-7e31.brighamhancock.workers.dev

## v0.10 — The Family Tree + deploy diagnostics (October 29, 2026)

**New:** [The Family Tree](https://odd-king-7e31.brighamhancock.workers.dev/connections/) lets fans select artists, explore directly sourced musician-project relationships, and calculate a shortest verified connection between two entries. The **Six Degrees of Jam** explorer shows each supporting source instead of implying undocumented sit-ins. It covers 52 verified relationship records among 55 artist/projects across eight components. Twenty-five unreviewed relationships are excluded from paths. All 52 verified links are present in the HTML itself, even with JavaScript disabled.

A long-standing broken-navigation issue on nested 404 URLs is corrected. The repository doctor now catches Git merge markers before they can corrupt the build. A read-only `python3 scripts/check_live.py` command checks **whether Cloudflare truly deployed this version**, rather than relying on successful local tests. The complete v0.10 source contains **50 tests** and builds **286 public routes** without fetching external data or using paid services.

See [INSTALL_V010_MAC.md](INSTALL_V010_MAC.md) for the full replacement workflow; keep your existing `.git` directory. Source and deployment are separate: copying files is not publication.

## v0.9 — Song Paths + complete-source release (October 28, 2026)

**New:** [Song Paths](https://odd-king-7e31.brighamhancock.workers.dev/song-paths/), a source-linked, server-rendered directory of **53 song titles and 106 documented show-excerpt appearances**. Search song titles, venue notes or dates; filter by performer or recurring titles; open the individual concert records; browse songs co-indexed in the same shows. Co-indexed songs are not proof of a segue or adjacent performance, and the dataset does not purport to be complete setlists.

This release contains the **entire GitHub-ready project**—not an incremental patch—including v0.1–v0.8 features, all data sources, scripts, GitHub workflows, tests and website configuration. It adds a source-tree diagnostic (`python3 scripts/doctor.py`) that explicitly checks version and the expected **37 test cases** before the build starts. Run `bash scripts/build_public.sh` to regenerate and validate **285 indexed URLs**; all build steps run locally with no external data fetch or paid service.

The previous release used [INSTALL_V09_MAC.md](INSTALL_V09_MAC.md); use the v0.10 installation guide for the current package. Keep your existing `.git` directory so that GitHub Desktop remains connected. The built `site/` folder is generated/ignored by Git. Cloudflare deployment still requires pushing through the existing GitHub-connected project.

## v0.8 — Time Machine / historical depth

**New:** [Time Machine](https://odd-king-7e31.brighamhancock.workers.dev/time-machine/), a static, source-backed timeline of **22 selected shows** from the original Allman Brothers Band (1969–1971) and the Grateful Dead's May 1977 run. It links to individual official show records, shows only evidenced setlist excerpts, and distinguishes recordings from performances.

The edition now contains **25 historic show dossiers, 17 external tape/release references, 53 song-title pages, 196 artists/projects, 77 relationships**, and a **45-event dated tour snapshot**. The historical catalog is still deliberately incomplete. Uncertain tape dates and missing setlists are disclosed; don't interpret missing links as evidence of a lost or nonexistent recording.

Human-curated seed data lives in `history_seed.py`; new independent research-agent additions require evidence and Git-tracked approval in `data/approved_recordings.json`. The new static page is generated by `build_v08.py`. Both the Time Machine and the Recording Explorer are linked from the homepage. No live API, third-party JavaScript, hosted music, or paid service is required.

Run `bash scripts/build_public.sh` (Python 3.11+ and Node.js needed). See `README-V08-PATCH.md` and `SOURCE_REVIEW_V08.md` for editorial scope and provenance.

## v0.7 — Recording Explorer and reproducible source review

The new [Recording Explorer](https://odd-king-7e31.brighamhancock.workers.dev/recordings/) groups the archive's documented source pages by performance, artist and recording type. It links to the original custodian and the concert dossier. **No audio is downloaded, copied or hosted.** The page originally started with nine curated source references; v0.8 adds eight official-release pointers verified from primary release documentation.

`data/approved_recordings.json` is the sole tracked publication feed for manually reviewed research-agent additions, while `history_seed.py` holds explicitly editor-curated founding concert and release records. A local `research.sqlite` or `research_queue.json` is **never** automatically promoted into public content. To propose a new approved external Internet Archive link:

1. Run the already configured, bounded manual source research or use `python3 research_agent.py sync --artists grateful-dead --limit 10 --contact 'your-public-project-contact@example.com'` (replace with a real contact; Internet Archive requests use this identification).
2. Run `python3 research_agent.py review list` and inspect the original source itself, its musician/date and the exact performance slot.
3. For an exact curated show, run `python3 research_agent.py review decision --id CANDIDATE_ID --verdict approve --show-id gd-1977-05-08 --note 'I checked the original archive page, performing artist, date and source notes.'` (substitute the actual candidate and show).
4. Run `python3 scripts/stage_approved.py --id CANDIDATE_ID`. This checks the prior manual approval and stages the source link in `data/approved_recordings.json`. It does **not** commit or deploy anything.
5. Run `bash scripts/build_public.sh`; inspect `site/recordings/index.html` and the related show page; review the changes to `data/approved_recordings.json` before committing to GitHub.

Staging currently supports only exact-date/artist Internet Archive candidates attached to an existing curated show. Early/late ambiguity and unrecognized creators require more research, never automatic assignment. Other custodians' source links may be entered into the tracked JSON only after documented editorial review and schema validation. A linked Archive page is not proof of audio quality, rights, or complete provenance.

## First steps

- [QUICK_START_MAC.md](QUICK_START_MAC.md): publish from GitHub Desktop or Terminal and connect the **existing** Cloudflare Worker.
- [GITHUB_TO_CLOUDFLARE.md](GITHUB_TO_CLOUDFLARE.md): detailed terminal and Cloudflare configuration.
- Run `bash scripts/build_public.sh` from this folder to regenerate all static pages, validate original content and links, and test the research code. Python 3 and Node.js required.
- `wrangler.jsonc`: static assets deployment configuration for `odd-king-7e31`. The public directory is generated at `site/` and must **not** be checked in.
- `.github/workflows/verify-static.yml`: independent validation on pushes and pull requests.
- `.github/workflows/daily-research.yml`: **manual-only** collection of review leads. Requires separately configured contact identity; never auto-publishes unverified discoveries.

The founding 110 entries are preserved, with 196 artist/project records, 77 connections, 25 curated historical concerts and 17 recording source pointers, 53 song pages, and 45 tour-event snapshot entries last checked October 26, 2026. The date is explicit so stale results aren't mistaken for live alerts.

See [DATA_RIGHTS.md](DATA_RIGHTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md). This project is independent and is not a registered nonprofit.

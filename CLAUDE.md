# The Jam Archive: working guide

Read this first. It's for anyone (human or AI) changing the site, and it's kept short on purpose.

**What it is:** a free, fan-built, source-first map of improvisational music (bands, musicians, shows, tapes) at https://thejamarchive.org. Static HTML, built by Python, hosted on a Cloudflare Worker (static assets only, no server code). The owner cares most about making the coolest, most accurate thing for the scene, and the Family Tree (who played with whom) is the flagship.

## Commands

```bash
bash scripts/build_public.sh   # full build + every check (~4s). Must pass before any push.
bash scripts/dev.sh            # full build, then serve at http://localhost:8000
bash scripts/dev.sh --quick    # build without checks, then serve (fast iteration)
```

Python 3.11+ and Node (only for `node --check`). No pip installs, no network at build time.

## Shipping a change

1. Branch from `main`; never commit to `main` directly.
2. `bash scripts/build_public.sh` must end with `BUILD: PASS`.
3. Push and open a PR. Two checks run: **Validate public Jam Archive** (GitHub Actions, same build) and **Workers Builds** (Cloudflare).
4. Cloudflare posts a preview on the PR at `https://<branch>-odd-king-7e31.brighamhancock.workers.dev`.
5. Merging to `main` deploys to production. If thejamarchive.org looks stale after a deploy, purge the zone cache in Cloudflare (Caching → Purge Everything).

## Adding to the Family Tree (the common edit)

Edit **`data/family_tree.json`**. Nothing else needs to change.

```json
{
  "entries": [{"name": "Page McConnell", "type": "person"}],
  "links": [
    {"from": "Page McConnell", "to": "Phish", "source": "https://…", "note": "1983–present"}
  ]
}
```

- `type` for entries: `person`, `band` or `project`. Ids are derived from names.
- `from`/`to` accept a display name, an alias or an id. `type` for links defaults to `member_of`; the other option is `collaboration_with`.
- **Every link needs an https `source` that actually states the relationship** (official band/artist site, label, reputable music press, Wikipedia as a last resort). Open the page and confirm it before adding. Never add a link from memory alone.
- A link here replaces any older unsourced placeholder for the same pair, which is how `needs_review` links become public.
- The build fails with a plain-English list of problems (unknown name, missing source, duplicate).
- Path-finding treats every link as an edge. Membership is not a sit-in: keep one-off guest appearances out of `member_of`.

## How the build works (and where to put changes)

The site grew as 14 release layers. `build_v014.py` runs `build_v013.py`, which runs `build_v012.py`, and so on down to `build_archive.py` → `seed_v01.py`. Each layer writes or patches files in `site/`. Then `build_public.sh` runs:

| Step | What it does |
|---|---|
| `build_v014.py` (→ whole chain) | Generates all pages and `site/assets/*.json` |
| `scripts/polish_site.py` | Global look (`jam_look.css`), mobile nav (`jam_experience.js`), copy tweaks |
| `scripts/presentation_fixes.py` | Homepage fixes: expiring listings, cleanup, layout fixes |
| `scripts/build_trails.py` | Story trails from `data/trails/*.json` → `/trails/<slug>/` (every section needs a source; every Family Tree path must exist) |
| `scripts/site_nav.py` | One menu on every inner page (edit `MAIN`/`MORE` there) + Family Tree card (bandmates, landmark paths) on artist pages |
| `validate.py`, `scripts/audit_site.py`, `tests/`, `safety_check.py`, `check_public_site.py` | Integrity, links, safety, tests |

Where data lives:
- Artists and relationships: `seed_v01.py` + `build_archive.py` (legacy, inline Python) **plus `data/family_tree.json` (preferred for all new additions)**, merged by `family_tree_data.py` inside `build_v03.py` (after every legacy entity list, so links can reference any existing name).
- Shows, studies, atlas: `history_seed.py`, `data/*.json`.
- Story trails: `data/trails/<slug>.json` (title, deck, sections with text + sources + an optional `path: [from_id, to_id]`).
- Homepage: `template.html` (a single-page app with tabs; the catalog is embedded as `const db={…}`).
- Family Tree (`/connections/`): page HTML, map layout and examples in `build_v010.py`; behavior in `connections.js`; styles in `connections.css`. The whole-web map is laid out at build time (deterministic), so it renders without JavaScript.

Rules of thumb:
- **New data goes in `data/`.** Don't add more inline lists to the legacy Python.
- **Prefer editing the layer that owns a page** over another string-replace patch. Patches (`str.replace`) fail silently when markup drifts; if you must patch, assert the target exists (see `presentation_fixes.py`'s `swap`).
- **Tests should check invariants, not counts.** Don't pin "exactly 77 relationships"; check that outputs match inputs.

## Gotchas

- `validate.py` requires the homepage to have exactly **4 inline `<script>`s**. Put new homepage JS inside an existing one or in an external file.
- `scripts/safety_check.py` fails closed on any new `wrangler.jsonc` key (prevents billable settings). `previews: {}` is allowed and must stay empty.
- `site/`, `catalog.json`, `index.html`, `*.sqlite` at the repo root are generated, so they're gitignored.
- Content Security Policy (`site/_headers`) blocks third-party scripts, fonts and images. Keep everything self-hosted.
- The tour snapshot in `build_archive.py` is dated; past events hide client-side.

## Editorial standards (non-negotiable)

- Unknown is better than invented. No inferred setlists, sit-ins or lineups.
- Link, don't copy. No hosted audio, no scraped databases, no band logos, album art or concert photos.
- Credit original sources (Phish.net, ABB show database, El Goose, Relisten, tapers). See `DATA_RIGHTS.md`.

## Docs

- `docs/history/`: old install guides, release notes and audits (v0.4–v0.14). Historical only.
- `docs/account-checklist.md`: Cloudflare/GitHub account hygiene.
- `CONTRIBUTING.md`, `DATA_RIGHTS.md`: public-facing policies.

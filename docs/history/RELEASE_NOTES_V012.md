# The Jam Archive — v0.12: Performance Lab + Whole-Site Quality Audit

**Release:** October 29, 2026 · Full static repository replacement, not a patch.

## What was added

- **Performance Lab** at `/performance-lab/`: 12 curated, source-linked historical sequence studies with 62 track positions, 18 *source-printed* transition marks, and 2 guest song credits. Includes four individual March 12–13 Fillmore East sets, its June 27 closing set, four selected Grateful Dead May 1977 concerts, and Phish on December 31, 1995.
- **Recording lineage explorer** at `/performance-lab/lineages/`: Allman Brothers 2014 Fillmore East box and Rhino's 2017 Betty Board chain, explicitly separating the live event from tapes, transfers, mastering and releases.
- **Cross-linking** from canonical concert dossiers to new performance evidence.
- **Consistent navigation** across all subpages, responsive horizontal section navigation for mobile, a functional keyboard skip link on every HTML page, focus states, and search control labels.
- **Tour snapshot honesty:** homepage now labels its schedule as the October 26, 2026 snapshot and dynamically hides entries whose stated event end date is past the browser's local date.
- **Offline audit** (`python3 scripts/audit_site.py`): checks HTML language, h1, landmarks, viewport, canonical URLs, accessible names, duplicate IDs, navigation, external script dependencies, target=blank security, image alt tags, 404 noindex and same-page fragments. Generated output: `site/assets/site_audit.json`.
- **Live deployment verification** (`python3 scripts/check_live.py`), including seven critical section pages and the actual HTTP 404 response.
- **Expanded test suite**: 79 unit tests.

## Source and interpretation policy

Sequence titles come from the referenced label's commercial release *track lists* or a cited community-curated setlist. A source-printed `>` or `->` symbol is replicated without independently inferring the musical boundaries, timing, improvisational type or similarity between performances. Guest credits are tied to a named song and cited source. Sources remain with their publishers; the archive hosts no audio or images from them.

Source links:
- Allman Brothers Band official discography: <https://allmanbrothersband.com/discography/the-1971-fillmore-east-recordings/>
- Rhino / Grateful Dead official release listing: <https://media.rhino.com/press-release/grateful-dead-place-two-titles-top-15-billboards-top-albums-chart>
- Phish.net 1995-12-31 editorial show entry: <https://phish.net/setlists/phish-december-31-1995-madison-square-garden-new-york-ny-usa.html>
- Phish official release: <https://phish.com/release/new-years-eve-1995/>

## Audit scope and remaining risks

The **compiled local website** passed structural and local-link checks. These checks cannot establish that every external source remains accessible, that the live Cloudflare deployment is up to date, that every user flow works in a real browser, or that all contrast and screen reader experiences pass. Neither a visual browser audit nor a live hosted-site crawl could be completed from this environment. Also, October 26 concert announcement data is **not live**. Updated verified announcements remain an important upcoming content priority.

No new hosted service, database binding, API key, subscription, scheduled collector, public account system or audio streaming was added. The local safety checker is not a Cloudflare billing or legal-rights certification.

## Development test

From repository root:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

After committing, pushing, passing GitHub Actions and seeing a Cloudflare Ready deployment:

```bash
python3 scripts/check_live.py
```

See `INSTALL_V012_MAC.md` for backup and installation steps.

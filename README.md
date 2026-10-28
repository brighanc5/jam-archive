# The Jam Archive

**Free · Fan-built · Source-first.** A public index of improvisational-music artists, performances, recordings and musical relationships. Historical and event data are incomplete research snapshots, not a live tour service.

**Live address:** https://odd-king-7e31.brighamhancock.workers.dev

## v0.7 — Recording Explorer and reproducible source review

The new [Recording Explorer](https://odd-king-7e31.brighamhancock.workers.dev/recordings/) groups the archive's documented source pages by performance, artist and recording type. It links to the original custodian and the concert dossier. **No audio is downloaded, copied or hosted.** The page starts with nine curated source references, and grows only after human review.

`data/approved_recordings.json` is the sole tracked publication feed for additional source links. A local `research.sqlite` or `research_queue.json` is **never** automatically promoted into public content. To propose a new approved external Internet Archive link:

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

The founding 110 entries are preserved, with 196 artist/project records, 77 connections, nine curated historical concerts and source pointers, 32 song pages, and 45 tour-event snapshot entries last checked October 26, 2026. The date is explicit so stale results aren't mistaken for live alerts.

See [DATA_RIGHTS.md](DATA_RIGHTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md). This project is independent and is not a registered nonprofit.

# The Jam Archive

**Free · Fan-built · Source-first.** A public index of improvisational-music artists, performances, recordings and musical relationships. Historical and event data are incomplete research snapshots, not a live tour service.

**Live address:** https://odd-king-7e31.brighamhancock.workers.dev

## First steps

- [QUICK_START_MAC.md](QUICK_START_MAC.md): publish from GitHub Desktop or Terminal and connect the **existing** Cloudflare Worker.
- [GITHUB_TO_CLOUDFLARE.md](GITHUB_TO_CLOUDFLARE.md): detailed terminal and Cloudflare configuration.
- Run `bash scripts/build_public.sh` from this folder to regenerate all static pages, validate original content and links, and test the research code. Python 3 and Node.js required.
- `wrangler.jsonc`: static assets deployment configuration for `odd-king-7e31`. The public directory is generated at `site/` and must **not** be checked in.
- `.github/workflows/verify-static.yml`: independent validation on pushes and pull requests.
- `.github/workflows/daily-research.yml`: **manual-only** collection of review leads. Requires separately configured contact identity; never auto-publishes unverified discoveries.

The founding 110 entries are preserved, with 196 artist/project records, 77 connections, nine curated historical concerts and source pointers, 32 song pages, and 45 tour-event snapshot entries last checked October 26, 2026. The date is explicit so stale results aren't mistaken for live alerts.

See [DATA_RIGHTS.md](DATA_RIGHTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md). This project is independent and is not a registered nonprofit.

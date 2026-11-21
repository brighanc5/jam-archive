# Publishing The Jam Archive v0.5

This project is a **free, independent fan archive**, not a registered charitable organization and not affiliated with the artists or archives.

## What you deploy

**Deploy the `site/` directory only.** It contains static HTML, CSS and JS. The public build contains no research SQLite file, secrets, or synthetic research fixture. It does contain the source-linked curated catalog in `assets/catalog.json`; this is a public index, not a blanket license to redistribute other archives' data.

Locally:

```bash
python3 build_v05.py
python3 validate.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory site
```

Then visit http://localhost:8000/. You can open `standalone_preview.html` without running a server, but persistent browser-local watchlist behavior is more dependable on a hosted origin. **No new recording or concert data is fetched by building the site.**

## Cloudflare Pages (static Git integration)

1. Create a GitHub repository containing the files in this project. Review all source data and rights before choosing a repository license.
2. In Cloudflare choose Pages → connect Git repository. Cloudflare's 2026 docs also recommend Workers for new full-stack applications, but this archive is currently static and Pages is sufficient.
3. Set **build command** to `python3 build_v05.py` and **build output directory** to `site`.
4. Publish to the temporary `*.pages.dev` address, then verify the artist, show, song and trail links plus the source disclaimers. There are **no server-side endpoints** to configure.
5. Once you own and have verified a domain, set build environment variable `JAM_ARCHIVE_ORIGIN=https://your-real-domain.example` (replace with your actual HTTPS origin), rebuild, and check the generated `site/sitemap.xml`, `site/robots.txt` and canonical tags. **Do not set a fictional domain** for testing.
6. Check site identity, attribution, and third-party permissions before inviting partners to contribute.

Reference: https://developers.cloudflare.com/pages/configuration/git-integration/ and https://developers.cloudflare.com/pages/framework-guides/deploy-anything/

## What this DOES NOT deploy

- No continually running research agent.
- No API keys, account registration, database write endpoints or real-time notifications.
- No streaming, downloading, or rehosting third-party concert audio.
- No public mechanism for submitting corrections yet. The `contribute/` page tells fans what the review process needs.
- The historical and tour records are narrow, static snapshots. They are **not** complete listings or live ticket availability.

The separate `.github/workflows/daily-research.yml` requires explicit repository configuration and a genuine contact identity. It produces a private-to-workflow review artifact; it does not publish claims automatically. See README v0.4 for that pipeline. We should not deploy automatic notifications before a verified, durable approvals database and better freshness checks exist.

## Minimum release checklist

- [ ] Run static validation and agent tests.
- [ ] Inspect profiles and show dossiers manually at desktop and mobile widths.
- [ ] Replace any incorrect source attribution and obtain permissions where required.
- [ ] Verify at least one link from each external archive category still resolves.
- [ ] Check source publication, license, attribution and privacy decisions.
- [ ] Remove or keep clearly labeled outdated tour events; never imply live data.
- [ ] Register and verify the real domain (or launch on `pages.dev`).
- [ ] Activate publishing only after checking the domain and source terms.

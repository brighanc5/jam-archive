# Put The Jam Archive online without GitHub

This release is a **static, noncommercial fan archive beta**. It can be hosted without linking a GitHub account or installing a JavaScript build system.

## Option A: direct ZIP upload to Cloudflare Pages

1. Download `jam_archive_v06_PUBLIC_SITE_UPLOAD.zip` — **not** the larger developer ZIP. It includes the ready-built site contents at the ZIP root (`index.html`, `artists/`, `shows/`, `songs/`, `assets/`, etc.). Do not unzip unless Cloudflare asks for a folder.
2. Sign in to your own Cloudflare account at https://dash.cloudflare.com/ . GitHub or Google authentication is **not required to connect a repository** for this path. If your authentication is blocked there as well, you can continue local development and publish later.
3. Open **Workers & Pages → Create application → Pages → Direct Upload / Drag and drop**. Names and menu layout may vary.
4. Choose a project name you like and upload the public-site ZIP. Select **Deploy site**.
5. Cloudflare provides an address ending in `.pages.dev`. Open it and test the homepage, a musician profile, a show page, a song page, the About page and the contribution form before announcing it publicly.
6. To update later, upload a new public-site ZIP through the same project's **Create deployment** action. This is a manual release process.

**Important architecture caveat:** a Cloudflare Pages project created via Direct Upload cannot later become a Git-integrated project. To get Git automation later, create a *new* Git-integrated project and move your custom domain. You can continue using Direct Upload with the Wrangler CLI independently of GitHub. Official documentation: https://developers.cloudflare.com/pages/get-started/direct-upload/

## Option B: local browsing, no account needed

1. Download and extract `jam_archive_v06_DEVELOPMENT.zip` (the full project).
2. Open Terminal and type `cd ` (include a space), drag the extracted folder into Terminal, and press Return.
3. Run `python3 local_server.py`. This script finds `site/` relative to its own location and opens a browser at a free local port. Press Control+C to stop.
4. Optionally double-click `OPEN_JAM_ARCHIVE.command` on macOS. Depending on macOS security settings, Terminal may be more reliable.

If you later edit source data, run `python3 build_v06.py`, `python3 validate.py`, and `python3 -m unittest discover -s tests -v` **from inside the project folder** before republishing.

## Publishing limitations

- These are static, dated concert and history snapshots, not real-time ticket inventory or alerts.
- The public ZIP contains **only website files**, not SQLite databases, Python research scripts, private review queue files or synthetic demo observations.
- The contribution form **downloads a research file locally** and does not submit it to a server. A moderation inbox or contact mechanism must be established later before soliciting submissions.
- Music and recording links go to original archives; this site does not host audio or transfer third-party rights.
- Confirm the project's name/domain availability, source terms and factual details before broad promotion.
- Once you receive a real production URL, set `JAM_ARCHIVE_ORIGIN=https://your-verified-site.example` in your shell and rerun `python3 build_v06.py`; this generates a matching sitemap and canonical metadata. Recreate the public-site ZIP afterward. Never use a fictional canonical address in a public release.

## Future automation

GitHub authentication is **not** a dependency for the site itself or the local research importer. We can later add Cloudflare-specific automation, a hosted moderation inbox, or GitHub/GitLab when those integrations are working. Do not automatically publish agent discoveries without source validation.

# The Jam Archive — origin-aware launch update (v0.6.1)

This update is built for the URL confirmed by the user through their 12/12 endpoint check:

https://odd-king-7e31.brighamhancock.workers.dev

## What changed

- Generated sitemap.xml referencing the actual production origin, not example addresses.
- robots.txt now points to the sitemap.
- Canonical page URLs for original artist/song/show/trail pages, homepage, About, and Contribute.
- No show, recording, artist or relationship data was changed by this SEO update.

## Redeploy without GitHub

Upload `jam_archive_v061_PUBLIC_SITE_UPLOAD.zip` as a new deployment to your **existing Cloudflare Worker static-assets project**. Do not create a new project unless you want another URL. The specific Worker upload control varies with how the original site was created. Make sure the ZIP contents (index.html, artists/, songs/, etc.) are deployed at the origin root, not within a containing directory.

After deployment, open:

- `/sitemap.xml` (must show <urlset> XML),
- `/robots.txt` (must link to the sitemap),
- `/artists/goose/` and `/shows/gd-1977-05-08/`.

Also manually verify: search returns results, stars survive refresh, Show Passport entries survive refresh, and the contribution form downloads JSON locally. The automated 12-endpoint check does not test browser interactivity or search-engine indexing.

## Rebuild from source

Extract the development project and run from its root:

```bash
JAM_ARCHIVE_ORIGIN=https://odd-king-7e31.brighamhancock.workers.dev python3 build_v061.py
python3 validate.py
python3 -m unittest discover -s tests -v
```

Package **only the contents of `site/`** for publication; never publish development SQLite files, internal queues, or research-agent fixtures. Update the origin if you later switch to a custom domain.

## Caveat

SEO metadata improves discoverability but does not guarantee that search engines will crawl or index the website. This is still a static historical/concert snapshot (as of 2026-10-26), not live alerts or a complete show database.

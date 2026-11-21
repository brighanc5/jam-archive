# Install The Jam Archive v0.14 on macOS

This ZIP includes the **complete repository**. No earlier patches are required.

1. In GitHub Desktop, select `brighanc5/jam-archive`, then **Repository → Show in Finder**. That opens the actual Git-connected folder, even if the name is `jam-archive 2`.
2. If GitHub Desktop shows an unfinished merge, resolve it before continuing. Duplicate the repository folder as a backup.
3. Extract `jam_archive_v014_COMPLETE_REPOSITORY.zip`. Open the folder inside the ZIP. In Finder, press **Command + Shift + .** to show `.github`.
4. Copy the contents of the extracted folder into the connected repository folder, replacing matching files; merge subfolders. **Keep the existing `.git` folder. Do not copy the parent folder inside the repository**. You don't need to copy the generated `site/` or temporary Python cache; the build regenerates those.
5. Open Terminal in the connected repository folder and run:

```sh
python3 scripts/doctor.py
bash scripts/build_public.sh
```

6. Confirm the full test suite passes and `PUBLIC CHECK PASS` is printed. GitHub Desktop: commit the changed source and push `main`.
7. In Cloudflare → Workers & Pages → `odd-king-7e31` → Deployments, confirm **a new Ready deployment** associated with that commit. Run `python3 scripts/check_live.py` to test the published domain.

The public URL is https://thejamarchive.org . New sections are `/show-depth/` and `/repertoire/`.

## On-phone checklist (important)

After deployment on an actual phone:

- Load homepage, Archive Atlas, Repertoire, and Family Tree; confirm the bottom navigation appears and doesn't cover the last item.
- Search `/era-atlas/` for `Fillmore`, tap **Show more gigs**, and confirm additional matching shows appear without resetting the filter.
- Open `/repertoire/`, tap **Keep digging**, then search for `Mountain Jam`. Confirm filters reset the number of shown cards and the result link opens a song page.
- On the homepage, tap **Discover**, then **Keep exploring** and confirm you can pass the first batch.
- Inspect a longer setlist in Show Studies and scroll to the source links; ensure nothing is cut off horizontally.
- Test Safari and Chrome where available, with VoiceOver if possible; test 320–390 px wide and landscape.

If a page looks wrong, record the page URL and a screenshot. Do not change Cloudflare hosting settings to fix a CSS or navigation issue.

# Install The Jam Archive v0.9 — full replacement (macOS)

**This is a complete source repository, not a patch.** It includes all prior features and 37 automated tests. The intended GitHub repository is `brighanc5/jam-archive`; the deployed Worker name remains `odd-king-7e31`.

## Before copying

1. Open **GitHub Desktop**. Select `jam-archive` under Current Repository and choose **Repository → Show in Finder**. **This Finder window is the correct Git repository folder**, regardless of whether its folder name is `jam-archive` or `jam-archive-2`.
2. Make a safe backup: use Finder to **duplicate that folder** outside the repo (e.g. on Desktop, name it `jam-archive-backup-before-v09`). Do not delete the current working repository or its `.git` folder.
3. Unzip `jam_archive_v09_COMPLETE_REPOSITORY.zip`. Open the **jam-archive-v0.9** folder inside the ZIP.
4. Press **Command+Shift+Period** in Finder to reveal hidden `.github` and `.git` folders. Select **everything inside** `jam-archive-v0.9` (including `.github`), and drag/copy it into the GitHub Desktop repository folder. Choose **Replace** for matching files. **Do not copy the enclosing `jam-archive-v0.9` folder into your repo.**
5. Do not delete or replace your existing repository's `.git` directory. **This ZIP does not include `.git`**; your existing GitHub connection remains intact.

This update overwrites every *matching* source file. Extra old files might remain (and may be reported by GitHub Desktop). Do **not** mass-delete unrecognized files; inspect them before removal. Build outputs in `site/` are regenerated automatically.

## Check the exact repository (do not skip)

In Finder, right-click the GitHub repository folder → **Services → New Terminal at Folder**. Or open Terminal and type `cd `, drag the folder from Finder into Terminal, then press Return.

```bash
pwd
python3 scripts/doctor.py
bash scripts/build_public.sh
```

Expected: doctor says `REPOSITORY DOCTOR PASS`, **37 tests** run and pass, `OVERNIGHT SAFETY PASS`, `PUBLIC CHECK PASS` with **285 URLs**, and `THE JAM ARCHIVE v0.9 FULL REPOSITORY BUILD: PASS`.

If doctor reports eight tests, you're almost certainly in a stale source folder or didn't merge the `tests` directory. Confirm with **GitHub Desktop → Repository → Show in Finder** and run the commands in **that** folder.

## Publish

Review changed files in GitHub Desktop, ensure no secrets/local databases are included, commit (e.g. `Release v0.9 full source and Song Paths`), then **Push origin**. Confirm the GitHub Actions validation succeeds, then confirm your existing Cloudflare production deployment is successful. Do not create a second Worker, repository, or paid service.

Live feature after successful deployment:

`https://odd-king-7e31.brighamhancock.workers.dev/song-paths/`

## Notes and limits

- Song Paths indexes **53 distinct titles and 106 documented show-excerpt appearances** in existing curated sources, not complete historical setlists. Co-listed songs are **not** proven to segue or be played back-to-back.
- Source research remains **manual only** and cannot autonomously publish. No concert audio/video is stored.
- Cloudflare may deploy from your connected GitHub project using `bash scripts/build_public.sh` and `site/`; this ZIP does not change its existing connection or billing settings. The policy file `_headers` is included in generated output, but actual header behavior must be checked on deployed Workers static assets.
- `site/`, `catalog.json`, and `jam_archive.sqlite` are generated output and excluded by `.gitignore`. All needed **source code, data, configuration, workflows, docs and tests** are in the ZIP.

# Install v0.13 on Mac — complete repository

This is the **full repository source**, not a patch. It does not overwrite your existing GitHub remote settings or Cloudflare Worker.

1. Open GitHub Desktop. Select **`jam-archive`** under Current Repository; use **Repository → Show in Finder**. This, not an old similarly named folder, is the actual working repository.
2. Check GitHub Desktop: if a pull, merge or rebase is still in progress, **resolve it before copying**. Do not force-push, delete `.git`, or blindly accept a whole-project remote overwrite.
3. Duplicate your working repository folder for backup. Keep its original `.git` untouched.
4. Extract `jam_archive_v013_COMPLETE_REPOSITORY.zip`, and open the enclosed **`jam-archive-v0.13`** directory.
5. In Finder, press **Command + Shift + .** to reveal hidden directories. Select **everything inside** `jam-archive-v0.13`, copy, then paste into the *repository folder GitHub Desktop opened*. Choose **Replace** for matching files. Do not nest `jam-archive-v0.13` inside the GitHub repo and do not copy over `.git`.
6. Open Terminal in the actual repository folder and run:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

Expect `REPOSITORY DOCTOR PASS`, `Ran 91 tests`, `OK`, `SITE QUALITY AUDIT: 673 HTML pages`, `OVERNIGHT SAFETY PASS`, `PUBLIC CHECK PASS: 672 URLs`, and `THE JAM ARCHIVE v0.13 ARCHIVE ATLAS FULL REPOSITORY BUILD: PASS`.

7. Open GitHub Desktop, inspect changes (especially `data/era_index.json`, `build_v013.py`, `scripts` and `.github`). Commit `Release v0.13 — Archive Atlas` and **Push origin**. Confirm `RELEASE_VERSION.txt` and `build_v013.py` are on the **main** branch of GitHub.
8. Wait until GitHub Actions validation passes and Cloudflare **Deployments** shows the corresponding new production commit as **Ready**. Cloudflare must run `bash scripts/build_public.sh`, because the generated `site/` directory is gitignored.
9. Run `python3 scripts/check_live.py` from the repository folder to verify the actual public deployment. The new page will be at `https://odd-king-7e31.brighamhancock.workers.dev/era-atlas/` once that deployment succeeds.

**If GitHub Desktop reports a merge conflict or the build reports fewer than 91 tests, stop before pushing and inspect the folder/merge state.** There is no need to change the Cloudflare Worker name, billing, or deploy credentials.

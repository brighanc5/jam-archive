# Install v0.11 on macOS — complete repository

**Important:** This ZIP is a complete source tree. It is **not** a patch. Do not create a second Git repository.

1. Open **GitHub Desktop**, select the `jam-archive` repository, then choose **Repository → Show in Finder**. This Finder window is the authoritative clone; its name might be `jam-archive-2`.
2. In GitHub Desktop, confirm there is **no unresolved merge or conflict**. If there is one, resolve it before copying files.
3. Duplicate the existing repository folder as a backup. A backup is useful because this is a full source replacement.
4. Unzip `jam_archive_v011_COMPLETE_REPOSITORY.zip` and open the enclosed `jam-archive-v0.11` folder.
5. Press **Command + Shift + .** in Finder to reveal hidden files such as `.github`.
6. Copy **all contents inside** `jam-archive-v0.11` into the repository folder GitHub Desktop opened. Choose **Replace** for matching files, and preserve existing `.git` (the ZIP does not include `.git`). Do **not** nest `jam-archive-v0.11` inside your repository.
7. Open Terminal at your actual repository folder, then run:

   ```bash
   python3 scripts/doctor.py
   bash scripts/build_public.sh
   ```

8. Confirm `REPOSITORY DOCTOR PASS`, `Ran 64 tests`, `OK`, `OVERNIGHT SAFETY PASS`, and `PUBLIC CHECK PASS: 309 URLs`.
9. In **GitHub Desktop**, inspect changes, commit `Release v0.11 — Deep Archive and reviewed research`, and click **Push origin**. If GitHub Desktop indicates merge conflicts, **stop** instead of using discard/force options.
10. Confirm **GitHub Actions** passes, and then confirm Cloudflare shows a **Ready** production deployment from the new commit.
11. After successful deployment, open `/deep-archive/` on your existing Worker URL. You may then run `python3 scripts/check_live.py` for an explicit server-side version check.

**Why the ZIP includes generated files:** They support local inspection; Git ignores `site/` and some regenerated root files. The Cloudflare build must regenerate them as part of deployment. A successful local build does not by itself change the live website.

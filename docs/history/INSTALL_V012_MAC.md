# Install v0.12 on Mac — full source replacement

1. In **GitHub Desktop**, select `jam-archive` and choose **Repository → Show in Finder**. This is the real Git repository regardless of whether its Finder folder is named `jam-archive` or `jam-archive-2`.
2. If GitHub Desktop indicates an unresolved merge, resolve or abort it *before* installing the replacement. Do not overwrite files while a merge is incomplete.
3. Duplicate the repository folder as a backup. The source ZIP does **not** include `.git` and must not replace or delete it.
4. Extract `jam_archive_v012_COMPLETE_REPOSITORY.zip`. Open the **inner** `jam-archive-v0.12` folder. Use **Command + Shift + .** to display the hidden `.github` folder.
5. Copy **everything inside** `jam-archive-v0.12` into the real repository folder, replacing files with the same names. **Never copy a second repository folder inside the current repository. Never overwrite `.git`.**
6. In Terminal, opened at the Git repository root, run:

   ```bash
   python3 scripts/doctor.py
   bash scripts/build_public.sh
   ```

   Expect `REPOSITORY DOCTOR PASS`, **79 passing tests**, `SITE QUALITY AUDIT ... 0 issues`, `OVERNIGHT SAFETY PASS`, and `PUBLIC CHECK PASS: 323 URLs`.
7. In GitHub Desktop, check the changed files, commit `Release v0.12 — Performance Lab and site audit`, and click **Push origin**. Check the latest GitHub Actions run and Cloudflare production deployment. If GitHub Desktop offers **Pull origin**, do not blindly merge another change—check whether the project has a merge in progress.
8. Verify production using:

   ```bash
   python3 scripts/check_live.py
   ```

The new public section is `/performance-lab/`; it will not work until the latest deployment is **Ready**.

**Important:** Generated `site/` content is ignored by Git, intentionally. Cloudflare's Git-connected build must run `bash scripts/build_public.sh` before `npx -y wrangler@4 deploy`. Do not attempt to commit the `site/` output manually.

# The Jam Archive v0.10 — safe Mac installation

This ZIP is **the complete project**, not a patch. It contains no `.git` directory. The live Cloudflare site will **not** change until the updated code is pushed to the correct GitHub repository and Cloudflare successfully builds/deploys it.

## 1. Make sure no merge is still unfinished

Open GitHub Desktop, select **brighanc5/jam-archive**, and look at the Changes tab. If it reports unresolved conflicts, a merge in progress, or a failed pull, **stop**; don't copy or pull more files over the top of it. Resolve the merge first or ask for assistance. Don't click "Discard all changes."

When GitHub Desktop is in an ordinary state, choose **Repository → Show in Finder**. Finder is now showing the **correct GitHub repository folder**, regardless of its name (`jam-archive`, `jam-archive-2`, etc.).

## 2. Back up and copy the complete project

1. Duplicate the repository folder in Finder, or make a separate ZIP backup; keep the backup outside the repository.
2. Unzip `jam_archive_v010_COMPLETE_REPOSITORY.zip`. Open the enclosed `jam-archive-v0.10` folder.
3. In Finder, press **Command + Shift + .** to show hidden files, including `.github`.
4. Select **everything inside** the `jam-archive-v0.10` folder, then copy those contents into the **existing** GitHub repository folder. Choose **Replace** for files with matching names.
5. **Do not delete or replace the repository's `.git` directory.** It is not included in the release ZIP. Do not create a fresh Git repository or change the Cloudflare Worker name.

The supplied files include the entire source, history, CSS, JS, `tests/`, `.github/`, and Worker config. The generated `site/` directory is included for inspection but deliberately ignored by Git; the actual deployment rebuilds `site/` from source.

## 3. Verify locally, then push

Open Terminal **inside the actual GitHub repository folder** (type `cd `, drag that folder into Terminal, press Return).

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

Expected:

```
REPOSITORY DOCTOR PASS
Ran 50 tests
OK
OVERNIGHT SAFETY PASS
PUBLIC CHECK PASS: 286 URLs
THE JAM ARCHIVE v0.10 FULL REPOSITORY BUILD: PASS
```

If you see `UNRESOLVED MERGE CONFLICT`, `MISSING`, or fewer than 50 discovered tests, **stop**. Do not push a broken tree.

Return to GitHub Desktop, review changes, commit with message `Release v0.10 — Source-backed Family Tree`, then **Push origin**. If Desktop says there is a merge/pull problem, do not blindly replace local changes; preserve the exact error message for debugging.

Check [GitHub Actions](https://github.com/brighanc5/jam-archive/actions) and Cloudflare Workers & Pages → `odd-king-7e31` → Deployments. The latest *new* deployment must be **Ready**.

## 4. Verify the site *actually* changed

In the same Terminal folder, run **after Cloudflare deploys**:

```bash
python3 scripts/check_live.py
```

It checks the **public website**, not your local files, and should print:

```
LIVE DEPLOYMENT PASS: v0.10 Family Tree and 404 fix are publicly served.
```

If it says "NOT DEPLOYED", the code has not reached the live Worker. If it says "COULD NOT VERIFY LIVE", check connectivity, Cloudflare access/challenges and the deployment dashboard.

Public feature URL: https://odd-king-7e31.brighamhancock.workers.dev/connections/

## Notes

- No new paid services, hosted audio, auto-publishing, cron jobs or external JavaScript were added.
- The Family Tree uses only the 52 `verified` relationship rows in the existing source catalog. Twenty-five research leads are excluded.
- The website has 286 sitemap routes, 25 historical shows, 17 indexed recording references and 53 song-title profiles in this release.
- The build remains offline. The optional `check_live.py` performs three small, read-only website requests **only when you run it**.

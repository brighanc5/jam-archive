# Quick start — The Jam Archive v0.12

For the **current** complete repository installation, read [INSTALL_V012_MAC.md](INSTALL_V012_MAC.md). The v0.9 instructions below are retained for historical reference only; do **not** follow their old ZIP filenames or test counts.

---

# Quick start on Mac — The Jam Archive v0.9

**You already have a GitHub repository and an existing Cloudflare Worker. Do not make a new one.**

1. Open GitHub Desktop → **Repository → Show in Finder** to find the **actual** repository folder. Its Finder name can be `jam-archive` or `jam-archive-2`.
2. Make a Finder duplicate of the repository folder as a backup.
3. Unzip **jam_archive_v09_COMPLETE_REPOSITORY.zip**, open the nested `jam-archive-v0.9` folder, reveal hidden files with **Command+Shift+Period**, and copy **all its contents** (including `.github`) into the real GitHub Desktop repository folder. Replace matching files. Do **not** replace `.git` (it is not in the ZIP).
4. Open Terminal in that repository folder and run:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

5. The doctor should confirm v0.9 and **37 tests**. The build should finish with **285 URLs** checked and a full-build pass.
6. In GitHub Desktop review the changes, commit, and **Push origin**. Check the validation and the existing Cloudflare deployment.

Read [INSTALL_V09_MAC.md](INSTALL_V09_MAC.md) for troubleshooting and caveats, including why you might have seen only eight tests previously.

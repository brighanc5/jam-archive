# Quick start — current v0.13 release

The supported workflow is to **update your existing GitHub Desktop repository**, not create another one. See [INSTALL_V013_MAC.md](INSTALL_V013_MAC.md) for the precise Finder/Terminal steps.

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

After those checks pass, commit and push in GitHub Desktop, confirm GitHub Actions, confirm a new Cloudflare **Ready** deployment, and run `python3 scripts/check_live.py`.

Do not delete or replace `.git`. If the project is mid-merge, resolve that before copying files.

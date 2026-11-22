# The Jam Archive — GitHub to existing Cloudflare Worker

Production Worker: `odd-king-7e31`
Live URL: https://odd-king-7e31.brighamhancock.workers.dev

## 1. Create the repository

On GitHub, create a **new empty repository** named `jam-archive` with no README, license, or .gitignore selected. Choose public only after reviewing `DATA_RIGHTS.md`; private works during setup too.

Download the **GitHub-ready ZIP** and unzip it. Open Terminal and enter the extracted folder by typing `cd ` and dragging the folder from Finder into Terminal (then Enter).

From the project root, run:

```sh
git init -b main
git add .
git commit -m "Found The Jam Archive public codebase"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/jam-archive.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your real GitHub username. To authenticate `git push`, use GitHub's supported credential manager, authenticated `gh`, or a personal access token when requested; **do not use your GitHub account password at the terminal prompt.** Never paste credentials into chat or commit them.

## 2. Connect to the *existing* Worker (don't make another)

Cloudflare Dashboard > Workers & Pages > `odd-king-7e31` > Settings > Builds > Connect > GitHub. Authorize the repository, choose branch `main`, and ensure root directory is `/` (project root).

**Build command:** `bash scripts/build_public.sh`
**Deploy command:** `npx -y wrangler@4 deploy`
**Preview command (optional):** `npx -y wrangler@4 versions upload`

`wrangler.jsonc` already targets the existing Worker. The build script defaults to your verified `workers.dev` hostname for sitemap/canonical generation.

### First production build

Cloudflare may deploy the latest commit when you connect, or on the next push. Check **Builds** for status; if needed push a small new commit, or use the dashboard's retry/build action. Do not delete your existing Worker.

## 3. Verify the result

Go to https://odd-king-7e31.brighamhancock.workers.dev and test search, followed artists, Cornell Show Passport, contribution export, and /sitemap.xml. Use the earlier 12-endpoint public checker if available.

## 4. Future updates

Edit your code locally, then run `bash scripts/build_public.sh` to test it before a push.
Commit and push to main to trigger an automatic Cloudflare build. GitHub Actions independently validates each push.

```sh
git add .
git commit -m "Describe the archive change"
git push
```

No public corrections endpoint or alert engine is active. The optional research workflow is deliberately **manual-only** and publishes nothing automatically. If we later change domains, update the `JAM_ARCHIVE_ORIGIN` build variable to the **actual verified domain**, rebuild, then check canonical/sitemap.

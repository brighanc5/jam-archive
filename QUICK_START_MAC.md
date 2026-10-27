# Start here: publish the archive from your Mac

This package contains an initialized **local Git repository** (`.git` is included), with **no remote and no GitHub credentials**. The main branch is `main`; the files have not yet been committed.

## A. Easiest: GitHub Desktop

1. Unzip this project. Move the extracted `jam-archive` folder somewhere permanent (for example, `~/Documents/Projects/jam-archive`), **not** into a temporary folder.
2. Install and sign in to [GitHub Desktop](https://desktop.github.com/).
3. **File → Add Local Repository**; choose the extracted `jam-archive` folder.
4. On the **Changes** tab, write a commit message such as `Initial Jam Archive release`, then click **Commit to main**.
5. Click **Publish repository**, use name `jam-archive`, and decide whether the repository should be public. Don't add a license until code/data rights have been reviewed.

## B. Terminal alternative (without GitHub Desktop)

1. On GitHub create a **new empty repository** called `jam-archive`: don't add README or license or .gitignore.
2. Navigate to your extracted folder (type `cd ` then drag folder into Terminal).
3. Run:

```bash
git add .
git commit -m "Initial Jam Archive release"
git remote add origin https://github.com/YOUR_USERNAME/jam-archive.git
git push -u origin main
```

Replace YOUR_USERNAME with your actual GitHub username. Git CLI may require a browser/credential-manager login or personal access token. **Never put a password or access token in a chat or source file.**

## C. Connect your existing Cloudflare Worker

In Cloudflare, choose Workers & Pages → Worker `odd-king-7e31` → Settings → Builds → Connect → GitHub. Select your `jam-archive` repository and main branch, project root `/`.

- Build: `bash scripts/build_public.sh`
- Deploy: `npx -y wrangler@4 deploy`
- Preview (optional): `npx -y wrangler@4 versions upload`

This builds the **existing** Worker at `https://odd-king-7e31.brighamhancock.workers.dev`; don't create a replacement Worker. Cloudflare might prompt for an app authorization.

See `GITHUB_TO_CLOUDFLARE.md` for troubleshooting and validation.

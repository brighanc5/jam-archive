# The Jam Archive — overnight safety patch

This patch contains only updated/new source files. It is **not a complete project**.
Copy the files into the same paths within your existing local `jam-archive` Git repository.

## What changes

- `build_v061.py`: installs reviewed `site/_headers` policy on every public build.
- `security_headers.txt`: restricts browser capabilities, remote scripts/connections,
  frames, embedded objects, and accidental HTML form posts; keeps existing inline
  scripts working (`'unsafe-inline'` remains until they are externalized).
- `scripts/safety_check.py`: refuses unknown Worker config keys, cron/scheduled research,
  local credentials, public databases, or concert audio/video in a generated site.
- `scripts/build_public.sh`: runs the safety tripwire after existing site/tests.
- `.github/workflows/verify-static.yml`: cancels superseded validation runs.

## Apply to your current repository

1. Extract this ZIP. In Finder, copy the included files into your existing local
   `jam-archive` repository, preserving subfolders and replacing matching files.
2. From a terminal **inside your existing repository folder**, run:

   ```sh
   bash scripts/build_public.sh
   git add build_v061.py security_headers.txt scripts/build_public.sh scripts/safety_check.py .github/workflows/verify-static.yml ACCOUNT_CHECKS.md
   git commit -m "Add zero-cost safety guardrails and static site protections"
   git push origin main
   ```

3. Confirm GitHub Actions is green and Cloudflare deployed; repeat your existing
   search/watchlist/passport/contribution browser checks. The new Content Security
   Policy has passed structural checks but has NOT passed real-browser interaction
   testing in this environment.

**Scope:** the safety scan checks source, not Cloudflare/GitHub account billing.
It does not mean the site is hacker-proof or immune from copyright complaints.

**Do not add** scheduled worker cron, paid AI/third-party APIs, server-side storage,
public audio hosting, or outbound email before making an explicit cost/rights
assessment. All music sources remain link-outs, pending provenance review.

**Account checks:** Cloudflare Workers plan must actually be Free; GitHub usage
budgets must block metered overages if configured; enable two-factor authentication
on both services and scope Cloudflare GitHub authorization to this repository.

# 5-minute owner-side account and rights checklist

These account settings CANNOT be established by examining source code.

- Cloudflare: dashboard -> Workers & Pages -> confirm Workers **Free** plan and inspect
  Billing / usage. The static project must have no paid add-ons or cron triggers.
  Never assume a notification email alone stops charges on a Paid plan.
- GitHub: Settings -> Billing & licensing -> Budgets and alerts. Set a relevant
  $0 spend budget (and enable **Stop usage when budget limit is reached** where
  supported) for any metered products you don't intend to use.
- GitHub / Cloudflare: enable two-factor authentication or a passkey; review
  authorized GitHub/Cloudflare integrations and restrict repository permissions.
- Repository: keep research metadata collection **workflow_dispatch only**.
  Do not store API keys, personal tokens, passwords, or `.env` files in Git.
- Publication: avoid band logos, concert photos, album covers, and audio files
  without specific permission. Keep citations and original archive links.
- Rights requests: document a responsive way to handle corrections or removal
  requests before soliciting broad third-party submissions. Formal DMCA safe-harbor
  eligibility may require designated agent registration and other conditions.
- Email: No outbound email service is configured. GitHub may still email you
  about workflow runs; this is GitHub notification behavior, not fan alerts.

No one can guarantee $0 spend, account immunity, or legal immunity from source
code inspection alone. This patch prevents certain classes of accidental source
changes while keeping those limits explicit.

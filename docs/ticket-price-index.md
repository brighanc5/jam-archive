# Ticket Price Index: plan and rules

Goal: on every upcoming show page, show where to buy tickets and, eventually, how the all-in price compares across sellers and how it has moved. The Jam Archive never sells tickets.

## Where we are

**Stage 1: done.**
- Every announced show lives in `data/upcoming_shows.json`, with a stable `id` that never changes once it's published.
- `scripts/build_upcoming.py` builds `/upcoming/` and `/upcoming/<id>/`. Each show page has the official link, the band's Family Tree and the band's other dates.
- Artist pages and the homepage's Live shows tab link to the show pages.
- Past dates are hidden in the browser, so the build stays deterministic.

The data model already has room for prices. Each show has these slots:

```json
"tickets": {"official_url": null},
"marketplace_ids": {"ticketmaster": "vvG1…", "tickpick": "…"},
"price_snapshots": [
  {"provider": "tickpick", "market": "resale", "all_in": true, "price_each": 84.5,
   "quantity": 2, "currency": "USD", "section": "GA floor",
   "captured_at": "2026-12-01T14:00:00Z", "url": "https://…", "affiliate": true}
]
```

`upcoming_shows.py` validates every field. A show page shows a price table only when `comparable_prices()` finds the latest all-in quote for the same number of tickets from **at least two** approved providers. One seller on its own is a link, not a comparison. Tests enforce this gate.

## Rules (non-negotiable)

- **Licensed feeds only.** No scraping, and no resellers of scraped data, unless the license explicitly covers republishing.
- **All-in prices only.** The FTC's fee rule (in force since May 12, 2025) requires advertised live-event ticket prices to include mandatory fees. The validator rejects any quote without `all_in: true`.
- **Compare like with like:** the same quantity together, and say which seats. Label primary (face value) versus resale.
- **Every quote shows when it was checked.** Never call a stored price "live".
- **Disclose affiliate links on the page** whenever one is shown. The code already does this. Cheapest-first order never changes for a commission.
- When the first affiliate link goes live, update the homepage line "Not for profit" and `DATA_RIGHTS.md`.

## Stage 2: price feeds (needs Brig)

1. **Apply for access.** These are account sign-ups only you can do:
   - **Ticketmaster Developer:** free Discovery API key. Gives event IDs and price ranges. `research_agent.py` already has a Ticketmaster adapter that feeds a review queue.
   - **TickPick affiliate:** advertises inventory APIs. This is the most promising first price feed.
   - **StubHub partner/affiliate:** API access is subject to approval. Second feed.
   - **SeatGeek / Vivid Seats:** later. Vivid Seats is a referral link only, at least to start.
2. **Pick an architecture.** Today the site is static assets only, and `safety_check.py` blocks cron triggers and billable bindings on purpose.
   - **(a) Snapshot at build time.** This is the recommended start. A script calls the approved APIs, writes `price_snapshots` into the data file, and the normal build publishes it. Run it by hand, or from a scheduled GitHub Action that opens a PR. It's cheap, reviewable and fits the static site. Prices are hours old and labeled with their time.
   - **(b) Worker + D1 + cron.** Prices are fresher and you get alerts, but it adds server code, storage and possible cost. It needs a deliberate change to the safety rules.
3. **Match events carefully.** Store each provider's event ID in `marketplace_ids`, and match on artist, venue and date. Never fuzzy-match.

## Stage 3: history and alerts

Keep every snapshot rather than only the latest, then chart the lowest comparable price over time. Alerts need accounts or email, which means a privacy review first.

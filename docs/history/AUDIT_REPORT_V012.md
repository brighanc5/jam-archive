# The Jam Archive — Whole-Site Audit · October 29, 2026

This report audits the **v0.12 compiled local site**, not the live Cloudflare deployment.

## Verified locally

- All 323 sitemap routes are backed by generated folder-index pages. A separate custom `404.html` remains unindexed.
- A static parser walked 324 HTML pages, inspected 5,605 internal/fragment asset references, and reported **zero remaining structural issues** after remediation.
- The separate public-site validator checks the local HTML file targets of links and assets, reconciles sitemap routes, and verifies that no local private database, source-code files, or review queue leaks into the public site.
- Content validation preserves the earlier 196 artist/project profiles, 25 historic-show pages, 53 song-title pages, 22 curated research dossiers, 21 recording pointers and 52 verified relationship graph edges.
- 79 automated Python tests exercise source citations, performance interpretation, graph links, public output, content review and smoke tests.
- The static-only safety tripwire still protects against accidental executable Workers, billable service bindings, automated research schedules, private files, and hosted concert audio/video.

## Issues resolved in v0.12

1. **Inconsistent primary navigation** between old artist pages and newer explorers: all subpages now use one sitewide navigation structure. This includes a responsive horizontal scroller on small screens.
2. **Keyboard navigation:** all generated pages now have a skip-to-main-content link and a named main landmark.
3. **Missing accessible names:** labeled the older home/search and recording-filter controls, and the repeat-only Song Paths checkbox. Other form fields use wrapping labels.
4. **Misleading current-schedule wording:** the home section identifies its October 26 snapshot and hides expired events at render time; this does not transform it into a live ticket feed.
5. **Inadequate audit coverage:** created a full-page HTML and accessibility-structure audit, checks content provenance and offers a production verification command.
6. **Weak recording provenance navigation:** 12 evidence excerpts and two source-grounded lineage walkthroughs now cross-link to the shows they describe.

## Data findings requiring future editorial work

- The October 26 tour snapshot had 45 dated entries, two of which had dates before October 29, 2026. Browser filtering fixes their presentation but **does not refresh the underlying source**.
- More than half the artist profiles still have little historical content; only ten artists have deep editorial dossiers. The archive should invest heavily in original research rather than merely expanding profile counts.
- There are 25 draft musician/project links requiring verification and eight disconnected verified graph components. No link should be fabricated to make the graph appear connected.
- The 12 new performance sequences capture only source-identified excerpts; they do **not** prove complete concert setlists, exact improvisational attributes, tape availability, or all credited personnel.

## Audit limits

- Web and browser automation here could not retrieve the live Workers site or GitHub repository, nor execute a reliable visual/mobile browser session. The **live deployed version and visual layouts remain unverified**, despite local success.
- Link checks confirm local targets but not the live availability, redirects or changing contents of third-party sources.
- CSS color-contrast ratios, real screen-reader navigation, and full end-to-end interaction should be manually or browser-automatically audited with access to a functioning browser environment.
- Published security headers are configured as Workers static `_headers`, a supported Cloudflare mechanism, but must be confirmed on the live response.

## Next priorities

1. Automated but **review-gated** source freshness, beginning with live artist announcements and releases, with explicit request caps.
2. Expand the primary-source show/track source set and document actual historical personnel by date.
3. Separate composition identities, recurring motifs, covers, segues and reprise relationships, only with reliable specific evidence.
4. Invite corrections using GitHub issues or reviewed data proposals; no unverified auto-publishing.

# The Jam Archive v0.13 — Archive Atlas

**Research release:** October 29, 2026. **Distribution:** complete GitHub-ready repository. **Deployment:** manual commit/push to the existing GitHub Desktop repository, followed by the connected Cloudflare production build.

## Delivered

- **361 distinct archived performance records**, of which **336 are newly added date-and-venue source pointers** and **25 are the preexisting, more deeply researched canonical show dossiers**. The new index includes 352 selected date entries, but 16 overlap dates already represented by an original detailed dossier. Overlaps link to the original page and are not counted twice.
- **12 historical chapter pages** across the Allmans' original era, the Grateful Dead in 1977, Phish's 1997–98 tours, and Goose's 2024 appearances.
- **20 source-attributed spotlights**, e.g. the Great Went, Phish's 1997 Denver performance, the 1998 Halloween musical costume, and the official 1970 Allmans Fillmore West milestone.
- **A new `/era-atlas/` explorer** with artist, year, evidence-level and full-text filters. All cards and chapter links are usable without JavaScript; filters are an enhancement.
- **336 permanent index-entry pages**, each with explicit source references, venue/date/location, and warnings that a source-indexed show is *not* proof of a complete setlist, lineup, guest appearance, taping or release.
- Artist profiles for the Allman Brothers Band, Grateful Dead, Phish and Goose gain dated history links.
- The previous Deep Archive, Performance Lab, Family Tree, Song Paths, Time Machine, recording catalog, and research queue remain unchanged.

## Editorial and source distinction

This archive maintains **two different levels of knowledge**:

1. **Detailed historical dossier** — a manually researched show entry with previously reviewed setlist excerpts, tape links and/or related research, linked to original sources.
2. **Date/venue source index** — the source confirms a documented calendar event and venue. We do *not* infer that any extant recording exists, that the full lineup was present, or that a publication's full setlist has been independently reviewed.

Source foundations: The Allman Brothers Band's official **1969, 1970 and 1971 concert databases**; the Grateful Dead's official 1977 show index; Phish.net **1997 Europe, 1997 US summer, 1997 fall, 1998 summer and 1998 fall** tour pages; and Goose Index's fan-maintained 2024 record, credited as derived from elgoose.net. Twenty highlights have additional setlist, memorabilia, or show-page citations. Exact URLs and coverage scope are stored in `data/era_index.json`.

**Limitations:** Only the listed source pages were inspected for the new base entries; this does not constitute a complete source audit of every show. ABB's official listing includes historical ambiguities and can change. Where a historical index has multiple sets on one date, v0.13's new pointer is date-level only; preexisting separate set dossiers remain separate. “Goose, November 24, 2024” is flagged as a brief appearance, not an asserted full headline performance. No new artist membership, guest credits, setlists, recording availability or song compositions were inferred. No rights-controlled music is copied or hosted. There is no background source crawling, and linked sites may change after review.

## Validation

Run these in the repository root:

```bash
python3 scripts/doctor.py
bash scripts/build_public.sh
```

The tested release reports:

- **91 unit tests passing**
- **672 distinct sitemap routes**
- **673 generated HTML pages** (includes non-indexed custom 404)
- **0 structural audit errors or warnings**
- **12,916 validated local HTML references** in the link validator
- `OVERNIGHT SAFETY PASS` and `PUBLIC CHECK PASS`

After pushing and a **Ready** Cloudflare deployment:

```bash
python3 scripts/check_live.py
```

This is a read-only production check; it does not deploy the site.

## Next high-value research

We have expanded the **concert index** dramatically. The next phase should upgrade selected entries from date/venue pointers to individual, traceable performance evidence: actual setlist sections, contemporaneous show sources, verifiable guest credits, and *separate* tape/transfer/release lineages. Priority should go to the ABB Fillmore era and the source gaps around pre-breakthrough Goose, plus better cross-artist musical connections.

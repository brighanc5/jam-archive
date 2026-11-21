# Archive Atlas editorial contract

The source-of-truth file for this release is `data/era_index.json`. Only human-reviewed entries enter this file. The build does not scrape third-party sites and requires no API key. Each record is an index-level pointer, not a completed concert dossier.

## Record fields

`id`: immutable, artist/date-based record ID. `artist_id`: key in the founding catalog. `date`: historical date in ISO format as attributed in the source index. `venue` and `place`: the referenced publication's identifying venue and location, normalized minimally. `era`: editorial series. `source_ids`: one or more source records in the same file. `evidence_scope: concert_date_venue`: explicitly limited verification. `songs: []`, `recording_status: not_investigated`, `lineup_status: not_investigated`: intentional unknowns, not negatives. `spotlight`: optional original short editorial text with its own source IDs.

Source classification is visible in `sources`: artist-official year index, independent community tour page, source-specific setlist, or artist-referenced historical memorandum. A community listing is not silently converted into an official statement.

## Before publishing a new record

- Verify that the band, date, venue, source title and URL refer to the same performance. If only an appearance/guest set is supported, state that explicitly.
- Check the existing `historical_shows` for a matching artist and date; where early/late sets exist, do **not** assume that a year-index entry identifies one particular set. Do not conflate festival billing dates, post-midnight playing time and recording-box labeling.
- If the source reports a cancellation, do not enter it as a completed concert. Use a separately labeled future 'scheduled/canceled event' model if needed.
- Never infer a recording or lineup from a concert calendar, or a segue from co-occurring song titles. Source commentary should remain under a separate `spotlight` entry with an explicit source.
- Keep quoted prose extremely short and prefer original paraphrase. Link to the source custodian; never copy, stream or rehost a rights-controlled recording.
- Rebuild and run the complete test suite. Manually inspect a sample of the new pages and source links. Do not claim that tests have verified every external URL; they validate internal consistency and URL structure.

## Open research tasks

Add original show-level source URLs where available (the year-level references currently point to a selection page); adjudicate multiple-set nights; add provenance for audio and official releases; attach confirmed guest credits at the performance level; research archival gaps in 1969 and early Goose. A reasonable next milestone is to convert 25 indexed-only shows into detailed reviewed dossiers using original event pages, release credits and taper-approved sources.


PRAGMA foreign_keys = ON;
CREATE TABLE entity (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL CHECK(type IN ('band','person','project')),
  origins_json TEXT NOT NULL, aliases_json TEXT NOT NULL);
CREATE TABLE source_seed (
  list_name TEXT NOT NULL, ordinal INTEGER NOT NULL, original_text TEXT NOT NULL,
  primary_entity_id TEXT NOT NULL REFERENCES entity(id), PRIMARY KEY(list_name, ordinal));
CREATE TABLE artist_relationship (
  source_entity_id TEXT NOT NULL REFERENCES entity(id), target_entity_id TEXT NOT NULL REFERENCES entity(id),
  relation TEXT NOT NULL, evidence_url TEXT, notes TEXT, verification TEXT NOT NULL,
  PRIMARY KEY (source_entity_id,target_entity_id,relation));
CREATE TABLE external_source (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL, source_type TEXT NOT NULL,
  access_notes TEXT NOT NULL, associated_entity_id TEXT REFERENCES entity(id));
-- Forward-compatible empty tables: NO LIVE SHOWS OR RECORDINGS ARE INGESTED YET.
CREATE TABLE event (
  id TEXT PRIMARY KEY, event_date TEXT NOT NULL, venue TEXT, city TEXT, region TEXT,
  country TEXT, timezone TEXT, event_status TEXT NOT NULL DEFAULT 'unverified',
  source_url TEXT, confirmed_at TEXT);
CREATE TABLE event_entity (
  event_id TEXT NOT NULL REFERENCES event(id), entity_id TEXT NOT NULL REFERENCES entity(id),
  billing_role TEXT NOT NULL DEFAULT 'performer', PRIMARY KEY (event_id,entity_id,billing_role));
CREATE TABLE recording (
  id TEXT PRIMARY KEY, event_id TEXT REFERENCES event(id), source_url TEXT NOT NULL,
  source_platform TEXT NOT NULL, recording_type TEXT, recording_lineage TEXT,
  permission_status TEXT NOT NULL DEFAULT 'unreviewed', metadata_verified TEXT NOT NULL DEFAULT 'unverified');
CREATE TABLE announcement (
  id TEXT PRIMARY KEY, headline TEXT NOT NULL, source_url TEXT NOT NULL,
  published_at TEXT, discovered_at TEXT NOT NULL, claim_status TEXT NOT NULL DEFAULT 'unverified');
CREATE TABLE announcement_entity (
  announcement_id TEXT NOT NULL REFERENCES announcement(id), entity_id TEXT NOT NULL REFERENCES entity(id),
  PRIMARY KEY (announcement_id, entity_id));
CREATE INDEX idx_seed_entity ON source_seed(primary_entity_id);
CREATE INDEX idx_rel_target ON artist_relationship(target_entity_id);
CREATE INDEX idx_event_date ON event(event_date);
CREATE INDEX idx_recording_event ON recording(event_id);

#!/usr/bin/env python3
"""Build the fan-first Jam Archive v0.1 founding catalog.
No third-party packages required; no live data downloads; no audio copied.
"""
import json, sqlite3, re, unicodedata, html
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent

# Each numbered entry is preserved verbatim as a SOURCE ROW, even when the
# entry names multiple independent musical entities.
main_rows = [
(1,"The Grateful Dead","Grateful Dead"),
(2,"Phish","Phish"),
(3,"The Allman Brothers Band","The Allman Brothers Band"),
(4,"Widespread Panic","Widespread Panic"),
(5,"Dave Matthews Band","Dave Matthews Band"),
(6,"The String Cheese Incident","The String Cheese Incident"),
(7,"Gov't Mule","Gov't Mule"),
(8,"Jerry Garcia Band","Jerry Garcia Band"),
(9,"moe.","moe."),
(10,"Yonder Mountain String Band","Yonder Mountain String Band"),
(11,"Blues Traveler/John Popper","Blues Traveler"),
(12,"Béla Fleck and the Flecktones","Béla Fleck and the Flecktones"),
(13,"The Black Crowes","The Black Crowes"),
(14,"The Disco Biscuits","The Disco Biscuits"),
(15,"Umphrey's Mcgee","Umphrey's McGee"),
(16,"Phil Lesh & Friends","Phil Lesh & Friends"),
(17,"Ratdog","RatDog"),
(18,"Keller Williams (Incident)","Keller Williams"),
(19,"Sound Tribe Sector 9","STS9"),
(20,"The Spin Doctors","Spin Doctors"),
(21,"Medeski, Martin & Wood","Medeski Martin & Wood"),
(22,"Little Feat","Little Feat"),
(23,"Oysterhead","Oysterhead"),
(24,"Trey Anastasio (Band/70 Volt Parade/GRAB)","Trey Anastasio"),
(25,"Tedeschi Trucks Band","Tedeschi Trucks Band"),
(26,"Galactic","Galactic"),
(27,"Dickey Betts & Great Southern","Dickey Betts & Great Southern"),
(28,"Old Crow Medicine Show","Old Crow Medicine Show"),
(29,"G. Love & Special Sauce","G. Love & Special Sauce"),
(30,"Les Claypool (& His Fancy Band/Fearless Flying Frog Brigade)","Les Claypool"),
(31,"Lotus","Lotus"),
(32,"Robert Randolph & The Family Band","Robert Randolph & the Family Band"),
(33,"New Riders of the Purple Sage","New Riders of the Purple Sage"),
(34,"Leftover Salmon","Leftover Salmon"),
(35,"My Morning Jacket","My Morning Jacket"),
(36,"Bruce Hornsby","Bruce Hornsby"),
(37,"Ween","Ween"),
(38,"The Drive-by Truckers","Drive-By Truckers"),
(39,"Primus","Primus"),
(40,"The Dirty Dozen Brass Band","Dirty Dozen Brass Band"),
(41,"Hot Tuna","Hot Tuna"),
(42,"Ben Folds Five","Ben Folds Five"),
(43,"Ben Harper & The Innocent Criminals","Ben Harper & the Innocent Criminals"),
(44,"Victor Wooten","Victor Wooten"),
(45,"The North Mississippi Allstars","North Mississippi Allstars"),
(46,"Rusted Root","Rusted Root"),
(47,"O.A.R.","O.A.R."),
(48,"Colonel Claypool's Bucket Of Bernie Brains","Colonel Claypool's Bucket of Bernie Brains"),
(49,"Benevento-Russo Duo (& Mike Gordon)","Benevento/Russo Duo"),
(50,"Man or Astroman?","Man or Astro-man?"),
(51,"Jack Johnson","Jack Johnson"),
(52,"Guster","Guster"),
(53,"Los Lonely Boys","Los Lonely Boys"),
(54,"Perpetual Groove","Perpetual Groove"),
(55,"Paul Butterfield Blues Band","Paul Butterfield Blues Band"),
(56,"Steve Kimock Band","Steve Kimock Band"),
(57,"John Butler Trio","John Butler Trio"),
(58,"Railroad Earth","Railroad Earth"),
(59,"Blind Melon","Blind Melon"),
(60,"Nickel Creek","Nickel Creek"),
(61,"Tea Leaf Green","Tea Leaf Green"),
(62,"Mike Gordon/Ramble Dove/Leo Kottke","Mike Gordon"),
(63,"Acoustic Syndicate","Acoustic Syndicate"),
(64,"The Big Wu","The Big Wu"),
(65,"Bernie Worrell and the WOO Warriors","Bernie Worrell & the WOO Warriors"),
(66,"The New Deal","The New Deal"),
(67,"Dispatch","Dispatch"),
(68,"Animal Liberation Orchestra","Animal Liberation Orchestra"),
(69,"Garaj Mahal","Garaj Mahal"),
(70,"Matisyahu","Matisyahu"),
(71,"Pat McGee Band","Pat McGee Band"),
(72,"Wishbone Ash","Wishbone Ash"),
(73,"Particle","Particle"),
(74,"Aquarium Rescue Unit","Aquarium Rescue Unit"),
(75,"The Derek Trucks Band","The Derek Trucks Band"),
(76,"Alfred Howard & The K23 Orchestra","Alfred Howard & the K23 Orchestra"),
(77,"Hot Buttered Rum String Band","Hot Buttered Rum"),
(78,"John Popper / John Popper Project feat. DJ Logic","John Popper"),
(79,"New Monsoon","New Monsoon"),
(80,"Fat Freddy's Drop","Fat Freddy's Drop"),
(81,"The Bad Plus","The Bad Plus"),
(82,"God Street Wine","God Street Wine"),
(83,"Antibalas Afrobeat Orchestra","Antibalas"),
(84,"Addison Groove Project","Addison Groove Project"),
(85,"Quicksilver Messenger Service","Quicksilver Messenger Service"),
(86,"Robert Walter's 20th Congress","Robert Walter's 20th Congress"),
(87,"The Word","The Word"),
(88,"The Samples","The Samples"),
(89,"Signal Path","Signal Path"),
(90,"The Breakfast","The Breakfast"),
(91,"MOFRO","MOFRO"),
(92,"Donna The Buffalo","Donna the Buffalo"),
(93,"RAQ","RAQ"),
(94,"Flowmotion","Flowmotion"),
(95,"Moonshine Still","Moonshine Still"),
(96,"Assembly of Dust","Assembly of Dust"),
(97,"Beanland","Beanland"),
(98,"Tri Point Paradox","Tri Point Paradox"),
(99,"Zilla","Zilla"),
(100,"Conspirator","Conspirator"),
(101,"Strangefolk","Strangefolk"),
(102,"Goose","Goose"),
(103,"Dopapod","Dopapod"),
(104,"Pigeons Playing Ping Pong","Pigeons Playing Ping Pong"),
(105,"Brothers Past","Brothers Past"),
(106,"Spafford","Spafford"),
(107,"Twiddle","Twiddle"),
(108,"Moon Taxi","Moon Taxi"),
(109,"Ghost Light","Ghost Light"),
(110,"The Heavy Pets","The Heavy Pets"),
]
precursor_rows = [
"Grateful Dead", "Cream", "The Allman Brothers Band", "Pink Floyd", "Deep Purple", "Frank Zappa", "Santana", "Jimi Hendrix", "Led Zeppelin", "The Yardbirds", "Blues Project"
]

# Person entities are separate from band/project entities. Includes lead artists
# whose live performances appear under their personal stage name.
main_people = {18,24,30,36,44,51,62,70,78}
extra_projects = [
("Billy Strings","person","related"),
("Joe Russo's Almost Dead","band","related"),
("Trey Anastasio Band","project","project"),
("70 Volt Parade","project","project"),
("G.R.A.B.","project","project"),
("Keller Williams Incident","project","project"),
("Les Claypool's Fancy Band","project","project"),
("Colonel Les Claypool's Fearless Flying Frog Brigade","project","project"),
("Ramble Dove","project","project"),
("Mike Gordon & Leo Kottke","project","project"),
("John Popper Project","project","project"),
("Benevento/Russo Duo with Mike Gordon","project","project"),
]
people = [
"Jimmy Herring", "Derek Trucks", "Rick Mitarotonda", "Warren Haynes", "Susan Tedeschi",
"Jerry Garcia", "Phil Lesh", "Bob Weir", "Les Claypool", "Trey Anastasio",
"Mike Gordon", "Stewart Copeland", "Marco Benevento", "Joe Russo", "Oteil Burbridge",
"John Popper", "Béla Fleck", "Leo Kottke", "DJ Logic", "Keller Williams", "Robert Randolph",
"John Medeski", "Jaimoe", "Billy Strings", "Dickey Betts"
]

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode('ascii')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')

entities = {}
def entity(name, typ="band", origin="related"):
    key = slug(name)
    if key in entities:
        existing = entities[key]
        if existing['name'] != name:
            raise ValueError(f"Slug collision {name} <> {existing['name']}")
        if existing['type'] != typ: raise ValueError(f"Type collision {name}: {typ} vs {existing['type']}")
        if origin not in existing['origins']: existing['origins'].append(origin)
        return key
    entities[key] = {"id":key,"name":name,"type":typ,"origins":[origin], "aliases":[]}
    return key

seed_rows = []
for i,raw,canonical in main_rows:
    k = entity(canonical, 'person' if i in main_people else 'band','founding')
    seed_rows.append({"list":"founding","number":i,"original":raw,"primary_id":k})

for i,name in enumerate(precursor_rows,1):
    k = entity(name, 'person' if name in {"Frank Zappa","Jimi Hendrix"} else 'band', 'precursor')
    seed_rows.append({"list":"precursor","number":i,"original":name,"primary_id":k})

for name,typ,origin in extra_projects: entity(name,typ,origin)
for name in people: entity(name,'person','musician')

aliases = {
"Grateful Dead":["The Grateful Dead"],
"The Allman Brothers Band":["ABB", "Allmans"],
"The String Cheese Incident":["SCI", "String Cheese"],
"Dave Matthews Band":["DMB"],
"Gov't Mule":["Gov’t Mule"],
"Widespread Panic":["Panic", "WP"],
"Tedeschi Trucks Band":["TTB"],
"Benevento/Russo Duo":["Benevento-Russo Duo", "The Duo"],
"Benevento/Russo Duo with Mike Gordon":["Benevento-Russo Duo feat. Mike Gordon"],
"STS9":["Sound Tribe Sector 9"],
"Medeski Martin & Wood":["Medeski, Martin & Wood", "MMW"],
"Trey Anastasio Band":["TAB"],
"G.R.A.B.":["GRAB", "Gordon Russo Anastasio Benevento"],
"Joe Russo's Almost Dead":["JRAD"],
"Pigeons Playing Ping Pong":["PPPP"],
"MOFRO":["JJ Grey & Mofro"],
"Antibalas":["Antibalas Afrobeat Orchestra"],
"Hot Buttered Rum":["Hot Buttered Rum String Band"],
"RatDog":["Ratdog"],
"Umphrey's McGee":["Umphrey's Mcgee"],
"John Popper Project":["John Popper Project feat. DJ Logic"],
"Colonel Les Claypool's Fearless Flying Frog Brigade":["Les Claypool's Fearless Flying Frog Brigade", "Fearless Flying Frog Brigade"],
}
for name, alias_list in aliases.items():
    entities[slug(name)]['aliases'] = alias_list

# Each source is ONLY a pointer to someone else's work. Nothing was scraped
# or republished here, and permission is NOT implied by being indexed.
sources = [
{"id":"abb-base","name":"ABBase / Official Allman Brothers Live Show Database","url":"https://allmanbrothersband.com/shows/","kind":"historical shows","entity":"The Allman Brothers Band","access":"link_only; inquire before bulk ingestion"},
{"id":"phishnet","name":"Phish.net API v5","url":"https://docs.phish.net/about-the-api","kind":"show history + setlists","entity":"Phish","access":"free noncommercial API under terms; request key; attribution; respect republication conditions"},
{"id":"lma","name":"Internet Archive Live Music Archive","url":"https://archive.org/details/etree","kind":"live recordings","entity":None,"access":"item-level/artist permissions vary; link to archive entries"},
{"id":"elgoose","name":"El Goose","url":"https://elgoose.net/","kind":"show history + setlists","entity":"Goose","access":"link_only; contact maintainers for dataset re-use"},
{"id":"panicstream","name":"PanicStream","url":"https://www.panicstream.com/","kind":"concert tapes + setlists","entity":"Widespread Panic","access":"link_only; site restricts other uses"},
{"id":"dmbalmanac","name":"DMB Almanac","url":"https://dmbalmanac.com/","kind":"historical show details","entity":"Dave Matthews Band","access":"link_only; contact maintainers for dataset re-use"},
{"id":"billybase","name":"BillyBase","url":"https://billybase.net/","kind":"show history + guests","entity":"Billy Strings","access":"link_only; contact maintainers for dataset re-use"},
{"id":"relisten","name":"Relisten","url":"https://relisten.net/","kind":"streaming discovery","entity":None,"access":"link_only; verify site/API access before integration"},
{"id":"musicbrainz","name":"MusicBrainz Web Service","url":"https://musicbrainz.org/doc/MusicBrainz_API","kind":"artist disambiguation","entity":None,"access":"free noncommercial with rate limit and identification; follow terms"},
{"id":"trey-oysterhead","name":"Trey Anastasio's Oysterhead Project Page","url":"https://trey.com/projects/oysterhead/","kind":"verified musician memberships","entity":"Oysterhead","access":"link_only"},
]

# Evidence-carrying relationships. A member-of edge may refer to a historical
# tenure, and absolutely does NOT imply an imminent gig, reunion, or sit-in.
rel = []
def r(a,b,kind="member_of", source="",notes="", verification="verified"):
    assert slug(a) in entities and slug(b) in entities, (a,b)
    rel.append({"from":slug(a),"to":slug(b),"type":kind,"source_url":source,"note":notes,"verification":verification})

r("Trey Anastasio","Phish",source="https://trey.com/about/")
r("Trey Anastasio","Oysterhead",source="https://trey.com/projects/oysterhead/")
r("Les Claypool","Oysterhead",source="https://trey.com/projects/oysterhead/")
r("Stewart Copeland","Oysterhead",source="https://trey.com/projects/oysterhead/")
r("Mike Gordon","Phish",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Trey Anastasio","G.R.A.B.",source="https://jambands.com/news/2006/07/24/phil-lesh-and-g-r-a-b-close-their-summer-tours-at-10-000-lakes/")
r("Mike Gordon","G.R.A.B.",source="https://jambands.com/news/2006/07/24/phil-lesh-and-g-r-a-b-close-their-summer-tours-at-10-000-lakes/")
r("Marco Benevento","G.R.A.B.",source="https://jambands.com/news/2006/07/24/phil-lesh-and-g-r-a-b-close-their-summer-tours-at-10-000-lakes/")
r("Joe Russo","G.R.A.B.",source="https://jambands.com/news/2006/07/24/phil-lesh-and-g-r-a-b-close-their-summer-tours-at-10-000-lakes/")
r("Marco Benevento","Benevento/Russo Duo",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Joe Russo","Benevento/Russo Duo",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Mike Gordon","Benevento/Russo Duo with Mike Gordon",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Marco Benevento","Benevento/Russo Duo with Mike Gordon",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Joe Russo","Benevento/Russo Duo with Mike Gordon",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Mike Gordon","Mike Gordon & Leo Kottke",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Leo Kottke","Mike Gordon & Leo Kottke",source="https://jambands.com/features/2024/06/26/for-sake-of-incredible-energy-and-smiley-ness-a-conversation-with-marco-benevento-and-mike-gordon/")
r("Derek Trucks","The Allman Brothers Band",source="https://www.laphil.com/people/tedeschi-trucks-band",notes="Joined in 1999, historical membership")
r("Derek Trucks","The Derek Trucks Band",source="https://www.laphil.com/people/tedeschi-trucks-band")
r("Derek Trucks","Tedeschi Trucks Band",source="https://www.laphil.com/people/tedeschi-trucks-band")
r("Susan Tedeschi","Tedeschi Trucks Band",source="https://www.laphil.com/people/tedeschi-trucks-band")
r("Warren Haynes","The Allman Brothers Band",source="https://news.pollstar.com/2014/01/09/trucks-haynes-leaving-allman-brothers-band/",notes="Historical membership")
r("Warren Haynes","Gov't Mule",source="https://news.pollstar.com/2014/01/09/trucks-haynes-leaving-allman-brothers-band/")
r("Jimmy Herring","The Allman Brothers Band",source="https://allmanbrothersband.com/event/abb20000616/",notes="Temporary touring guitarist, summer 2000; not an uninterrupted permanent lineup")
r("Keller Williams","Keller Williams Incident",source="https://jambands.com/news/2019/01/28/the-string-cheese-incident-collaborate-with-keller-williams-in-jamaica/")
r("Keller Williams Incident","The String Cheese Incident",kind="collaboration_with",source="https://jambands.com/news/2019/01/28/the-string-cheese-incident-collaborate-with-keller-williams-in-jamaica/")
r("Trey Anastasio","Trey Anastasio Band",source="https://www.laphil.com/people/trey-anastasio")
r("Trey Anastasio","70 Volt Parade",verification="needs_review",notes="Project cross-reference from user's founding list")
r("Les Claypool","Primus",source="https://trey.com/projects/oysterhead/")
r("Les Claypool","Les Claypool's Fancy Band",verification="needs_review")
r("Les Claypool","Colonel Les Claypool's Fearless Flying Frog Brigade",verification="needs_review")
r("Les Claypool","Colonel Claypool's Bucket of Bernie Brains",verification="needs_review")
r("John Popper","Blues Traveler",verification="needs_review")
r("John Popper","John Popper Project",verification="needs_review")
r("DJ Logic","John Popper Project",kind="collaboration_with",verification="needs_review")
r("Jerry Garcia","Grateful Dead",verification="needs_review")
r("Jerry Garcia","Jerry Garcia Band",verification="needs_review")
r("Phil Lesh","Grateful Dead",verification="needs_review")
r("Phil Lesh","Phil Lesh & Friends",verification="needs_review")
r("Bob Weir","Grateful Dead",verification="needs_review")
r("Bob Weir","RatDog",verification="needs_review")
r("Béla Fleck","Béla Fleck and the Flecktones",verification="needs_review")
r("Robert Randolph","Robert Randolph & the Family Band",verification="needs_review")
r("Jimmy Herring","Widespread Panic",verification="needs_review")
r("Jimmy Herring","Aquarium Rescue Unit",verification="needs_review")
r("Joe Russo","Joe Russo's Almost Dead",verification="needs_review")
r("Marco Benevento","Joe Russo's Almost Dead",verification="needs_review")
r("Rick Mitarotonda","Goose",verification="needs_review")
r("Dickey Betts","Dickey Betts & Great Southern",verification="needs_review")
r("Dickey Betts","The Allman Brothers Band",verification="needs_review")
r("Oteil Burbridge","The Allman Brothers Band",verification="needs_review")
r("Jaimoe","The Allman Brothers Band",verification="needs_review")
r("John Medeski","Medeski Martin & Wood",verification="needs_review")

SCHEMA = """
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
"""

def create_database(path):
    if path.exists(): path.unlink()
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    with db:
        db.executemany("INSERT INTO entity VALUES (?,?,?,?,?)", [(e['id'], e['name'],e['type'],json.dumps(e['origins']),json.dumps(e['aliases'])) for e in entities.values()])
        db.executemany("INSERT INTO source_seed VALUES (?,?,?,?)", [(r['list'],r['number'],r['original'],r['primary_id']) for r in seed_rows])
        db.executemany("INSERT INTO artist_relationship VALUES (?,?,?,?,?,?)", [(r['from'],r['to'],r['type'],r['source_url'],r['note'],r['verification']) for r in rel])
        db.executemany("INSERT INTO external_source VALUES (?,?,?,?,?,?)",[(s['id'],s['name'],s['url'],s['kind'],s['access'],slug(s['entity']) if s['entity'] else None) for s in sources])
    integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
    assert integrity == 'ok', integrity
    assert db.execute('SELECT count(*) FROM source_seed WHERE list_name="founding"').fetchone()[0] == 110
    assert db.execute('SELECT count(*) FROM source_seed WHERE list_name="precursor"').fetchone()[0] == 11
    assert db.execute('SELECT count(*) FROM event').fetchone()[0] == 0
    db.close()

out = {"about":{"project":"The Jam Archive","version":"0.1 founding registry","as_of":"2026-10-26","disclaimer":"Seeded artist list and manually curated musician relationships. NO live concerts, setlists, recordings or tour alerts are ingested. All source links point externally. Sources require permissions review before bulk ingestion."}, "entities":list(entities.values()), "source_entries":seed_rows,"relationships":rel,"sources":sources}
(ROOT/'catalog.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'schema.sql').write_text(SCHEMA,encoding='utf-8')
create_database(ROOT/'jam_archive.sqlite')

# The offline web explorer includes its full catalog inline, so it works when
# opened directly as a file. Follow selections are stored ONLY in localStorage.
payload = json.dumps(out,ensure_ascii=False).replace('</','<\\/')
html_content = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Jam Archive — Founding Registry</title>
<style>
:root{color-scheme:dark;--bg:#0b1115;--panel:#111c20;--ink:#e7eadd;--muted:#96a9a4;--line:#30413f;--lime:#cef091;--gold:#f0b974;--teal:#65caba}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse 76% 46% at 95% 3%,#203b38 0%,transparent 67%),var(--bg);color:var(--ink);font-family:system-ui,-apple-system,Segoe UI,sans-serif}a{color:var(--teal)}a:hover{color:var(--lime)}.frame{width:min(1200px,92vw);margin:auto}.topbar{display:flex;justify-content:space-between;align-items:center;padding:25px 0;border-bottom:1px solid var(--line)}.brand{font-weight:850;letter-spacing:.08em;font-size:15px;text-transform:uppercase}.brand b{color:var(--lime)}.topbar small{color:var(--muted)}.hero{padding:64px 0 38px;max-width:980px}.eyebrow{font-size:11px;letter-spacing:.19em;color:var(--lime);text-transform:uppercase;font-weight:800}.hero h1{font-size:clamp(43px,8vw,97px);line-height:.95;font-weight:820;letter-spacing:-.065em;margin:15px 0 24px}.hero h1 em{font-style:normal;color:var(--lime)}.hero p{max-width:710px;color:var(--muted);font-size:17px;line-height:1.6}.stats{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:14px;margin:26px 0 37px;background:#101a1b}.metric{padding:22px 24px;border-right:1px solid var(--line)}.metric:last-child{border-right:0}.metric strong{font-size:32px;letter-spacing:-.06em;display:block}.metric span{color:var(--muted);font-size:12px}.layout{display:grid;grid-template-columns:1fr 285px;gap:30px}.section-title{font-size:26px;letter-spacing:-.035em;margin:14px 0 5px}.section-kicker{color:var(--muted);font-size:14px;margin:0 0 22px}.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:19px}.search{background:#17272a;border:1px solid #355152;border-radius:8px;color:var(--ink);padding:12px 13px;min-width:220px;flex:1;font-size:14px;outline:none}.search:focus{border-color:var(--lime)}.filter{padding:10px 12px;border-radius:8px;border:1px solid #344b4a;background:#142123;color:var(--muted);cursor:pointer}.filter.active{background:var(--lime);color:#152019;font-weight:750;border-color:var(--lime)}.list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}.artist{border:1px solid var(--line);padding:17px;background:#101a1c;border-radius:12px;min-height:117px}.artist-head{display:flex;gap:8px;justify-content:space-between}.artist-name{font-size:17px;font-weight:760;line-height:1.2}.star{font-size:22px;min-width:31px;min-height:31px;cursor:pointer;background:transparent;border:1px solid #45615a;border-radius:9px;color:var(--muted)}.star.followed{background:#2f4335;color:var(--lime);border-color:var(--lime)}.meta{display:flex;gap:6px;flex-wrap:wrap;margin:9px 0 11px}.chip{font-size:11px;border-radius:5px;background:#1d3030;border:1px solid #2f4543;color:#b9cec6;padding:3px 7px}.description{font-size:12px;color:var(--muted);line-height:1.5}.artist a{font-size:12px;display:inline-block;margin:5px 10px 0 0}.aside{position:sticky;top:22px;align-self:start;display:flex;flex-direction:column;gap:14px}.panel{border:1px solid var(--line);background:var(--panel);border-radius:14px;padding:21px}.panel h3{font-size:16px;margin:0 0 12px}.panel p,.panel li{font-size:13px;color:var(--muted);line-height:1.6}.panel ul{padding-left:18px}.panel .emphasis{color:var(--lime);font-weight:750}.panel small{color:var(--muted)}.source-link{display:block;font-size:13px;padding:8px 0;border-bottom:1px solid var(--line)}.source-link:last-child{border:0}.footer{padding:50px 0 30px;font-size:12px;color:var(--muted);line-height:1.7}.empty{padding:26px;border:1px dashed var(--line);border-radius:9px;color:var(--muted)}.tag{display:inline-block;color:var(--gold)}@media(max-width:850px){.layout{grid-template-columns:1fr}.aside{position:static}.stats{grid-template-columns:repeat(2,1fr)}.metric:nth-child(2){border-right:0}.metric:nth-child(-n+2){border-bottom:1px solid var(--line)}}@media(max-width:520px){.list{grid-template-columns:1fr}.hero{padding:45px 0 18px}.hero h1{font-size:53px}.topbar small{display:none}}
</style></head><body>
<div class="frame"><header class="topbar"><div class="brand">THE <b>JAM</b> ARCHIVE <span style="color:var(--muted);font-weight:400">/ founding edition</span></div><small>Free. Fan-built. Source-first.</small></header>
<section class="hero"><div class="eyebrow">Live music is a living history</div><h1>Every show.<br>Every connection.<br><em>One place.</em></h1><p>Our first working catalog of the improvisational music universe: 110 founding entries, the musical roots they came from, and the players whose projects connect them. This is a local browsing prototype, not yet a live concert or recording index.</p></section>
<section class="stats"><div class="metric"><strong id="count-founders">110</strong><span>Founding entries</span></div><div class="metric"><strong>11</strong><span>Historical influences (2 overlaps)</span></div><div class="metric"><strong id="count-entities">—</strong><span>Distinct catalog entities</span></div><div class="metric"><strong id="count-rel">—</strong><span>Documented / draft relationships</span></div></section>
<section class="layout"><div><h2 class="section-title">The collection</h2><p class="section-kicker">Search the universe. Star artists for a browser-local watchlist.</p><div class="tools"><input id="search" class="search" type="search" placeholder="Search Phish, Herring, Oysterhead, STS9…" aria-label="Search artists"><button class="filter active" data-filter="all">All</button><button class="filter" data-filter="founding">Founding</button><button class="filter" data-filter="precursor">Roots</button><button class="filter" data-filter="project">Side projects</button><button class="filter" data-filter="person">Musicians</button><button class="filter" data-filter="followed">Following</button></div><div class="list" id="list"></div><div class="empty" id="empty" style="display:none">No artists match that search.</div><p id="result-count" style="color:var(--muted);font-size:12px;margin-top:17px"></p></div>
<aside class="aside"><div class="panel"><div class="eyebrow">Watchlist</div><h3 style="margin-top:10px">Your followed artists</h3><p id="follows-copy">Tap ☆ on any artist to save them here.</p><p style="color:var(--gold)">Tour alerts are not yet running. Stars are saved only in this browser.</p></div><div class="panel"><div class="eyebrow">The graph in action</div><h3 style="margin-top:10px">Oysterhead isn't one artist</h3><p>Its connection to <span class="emphasis">Trey Anastasio</span>, <span class="emphasis">Les Claypool</span> and <span class="emphasis">Stewart Copeland</span> means we can eventually recognize related projects and relevant announcements.</p><p>Similarly, Derek Trucks connects the Allmans, the Derek Trucks Band and Tedeschi Trucks Band.</p></div><div class="panel"><div class="eyebrow">Archive partners to explore</div><h3 style="margin-top:10px">Source directory</h3><div id="source-links"></div><p>Links are pointers, not permissions to copy content.</p></div><div class="panel"><h3>Preservation principle</h3><p>Every eventual show or recording needs a date, performer, original source, attribution, and verification status. Unknown is better than invented.</p></div></aside></section>
<footer class="footer">The Jam Archive · v0.1 seed prototype · Created 2026-10-26. No third-party artist data scraped into this catalog. No touring dates or streaming audio are included. This is an independent, unofficial community concept, not affiliated with the musicians or source sites listed.</footer></div>
<script>window.JAM_DATA=__CATALOG_PAYLOAD__;</script><script>
const db=window.JAM_DATA; let filter='all';let term='';const el=(id)=>document.getElementById(id);let favorites;try{favorites=new Set(JSON.parse(localStorage.getItem('jam-watch-v1')||'[]'))}catch(e){favorites=new Set()}
const relationMap={};for(const r of db.relationships){(relationMap[r.from] ||= []).push(r);(relationMap[r.to] ||= []).push(r)};
const seeds={};for (const s of db.source_entries){(seeds[s.primary_id] ||= []).push(s)};
const sourceMap={};for(const s of db.sources){if(s.entity)(sourceMap[s.entity.toLowerCase()] ||= []).push(s)};
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function display(e){let roots=e.origins.includes('precursor'),founding=e.origins.includes('founding');let badges=[e.type==='person'?'musician':e.type,founding?'founding':roots?'historical roots':e.origins.includes('project')?'project extension':'related artist'];if(roots&&founding)badges.push('also a precursor');let rels=(relationMap[e.id]||[]).filter(x=>x.verification==='verified').slice(0,3).map(x=>{let other=x.from===e.id?x.to:x.from;return db.entities.find(q=>q.id===other)?.name}).filter(Boolean);const links=(sourceMap[e.name.toLowerCase()]||[]).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.name.replace(/\s+(Live Show Database|Project Page)$/,''))} ↗</a>`).join('');return `<article class="artist"><div class="artist-head"><div class="artist-name">${esc(e.name)}</div><button class="star ${favorites.has(e.id)?'followed':''}" data-id="${esc(e.id)}" aria-label="Toggle watchlist for ${esc(e.name)}" title="Follow or unfollow">${favorites.has(e.id)?'★':'☆'}</button></div><div class="meta">${badges.map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div>${rels.length?`<div class="description">Connected: ${esc(rels.join(' · '))}</div>`:''}${links?`<div>${links}</div>`:''}</article>`}
function render(){const matches=db.entities.filter(e=>{const origins=e.origins;let ok=filter==='all'||filter==='followed'&&favorites.has(e.id)||filter==='project'&&e.type==='project'||filter==='person'&&e.type==='person'||origins.includes(filter);let hay=(e.name+' '+e.aliases.join(' ')+' '+(seeds[e.id]||[]).map(x=>x.original).join(' ')).toLowerCase();return ok&&hay.includes(term)}).sort((a,b)=>a.name.localeCompare(b.name));el('list').innerHTML=matches.map(display).join('');el('empty').style.display=matches.length?'none':'block';el('result-count').textContent=`Showing ${matches.length} of ${db.entities.length} distinct entities`;el('follows-copy').textContent=favorites.size?`${favorites.size} artist${favorites.size===1?'':'s'} followed: ${[...favorites].map(id=>db.entities.find(e=>e.id===id)?.name).filter(Boolean).slice(0,12).join(', ')}${favorites.size>12?'…':''}`:'Tap ☆ on any artist to save them here.';document.querySelectorAll('.star').forEach(b=>b.addEventListener('click',()=>{favorites.has(b.dataset.id)?favorites.delete(b.dataset.id):favorites.add(b.dataset.id);try{localStorage.setItem('jam-watch-v1',JSON.stringify([...favorites]))}catch(e){}render()}))}
el('count-entities').textContent=db.entities.length;el('count-rel').textContent=db.relationships.length;el('source-links').innerHTML=db.sources.filter(s=>s.entity).map(s=>`<a class="source-link" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.name)} ↗</a>`).join('');el('search').addEventListener('input',e=>{term=e.target.value.trim().toLowerCase();render()});document.querySelectorAll('.filter').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.filter;render()}));render();
</script></body></html>
'''
(ROOT/'index.html').write_text(html_content.replace('__CATALOG_PAYLOAD__',payload),encoding='utf-8')
print(json.dumps({"founding_rows":len(main_rows),"precursor_rows":len(precursor_rows),"unique_primary":len({r['primary_id'] for r in seed_rows}),"entities":len(entities),"relationships":len(rel),"sources":len(sources)},indent=2))

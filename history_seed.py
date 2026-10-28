"""Small hand-curated source-linked v0.3 history seed. Excerpts are not full setlists.
Recordings are external pointers only. A recording link is not a license to rehost.
"""
H=[]
def show(id,artist,date,venue,city,region,source,highlight,songs,slot='',notes=''):
 H.append(dict(id=id,artist=artist,date=date,venue=venue,city=city,region=region,source_url=source,
  highlight=highlight,songs=songs,slot=slot,notes=notes,verification='source_linked',
  data_checked='2026-10-26',setlist_scope='Selected songs; not the complete setlist'))
abb='The Allman Brothers Band'
show('abb-1971-03-12-early',abb,'1971-03-12','Fillmore East','New York','NY','https://allmanbrothersband.com/event/abb19710312/',
 'Fillmore East early show; one of several distinct performances recorded during the run.',
 ['Statesboro Blues','Trouble No More',"Don’t Keep Me Wonderin’",'In Memory of Elizabeth Reed','You Don’t Love Me'],'Early show', 'The official database lists separate early and late shows; approximate times are not authoritative.')
show('abb-1971-03-12-late',abb,'1971-03-12','Fillmore East','New York','NY','https://allmanbrothersband.com/event/abb19710312a/',
 'Late show from the celebrated Fillmore East recording run.',
 ['Statesboro Blues','Trouble No More','In Memory of Elizabeth Reed','Whipping Post',"Hot ’Lanta"],'Late show','Official recording compilation documents selections from this performance.')
show('abb-1971-03-13-early',abb,'1971-03-13','Fillmore East','New York','NY','https://allmanbrothersband.com/event/abb19710313/',
 'First of two separately indexed Allman Brothers performances this evening.',
 ['Statesboro Blues','Trouble No More','In Memory of Elizabeth Reed','You Don’t Love Me','Whipping Post'],'Early show')
show('abb-1971-03-13-late',abb,'1971-03-13','Fillmore East','New York','NY','https://allmanbrothersband.com/event/abb19710313a/',
 'The late performance includes Mountain Jam and a guest appearance by Elvin Bishop.',
 ['Statesboro Blues','One Way Out','Stormy Monday','Whipping Post','Mountain Jam','Drunken Hearted Boy'],'Late show')
show('abb-1971-06-27',abb,'1971-06-27','Fillmore East','New York','NY','https://allmanbrothersband.com/event/abb19710627/',
 'Fillmore East closing concert, represented on an official archival release.',
 ['Statesboro Blues','One Way Out','Midnight Rider','Whipping Post','You Don’t Love Me'],'Closing night')
show('abb-2014-10-28',abb,'2014-10-28','Beacon Theatre','New York','NY','https://allmanbrothersband.com/event/abb20141028/',
 'The Allman Brothers Band final concert, with an authorized official recording.',
 ['Little Martha','Mountain Jam','Blue Sky','Melissa','In Memory of Elizabeth Reed','Whipping Post'],'Final concert')
show('gd-1977-05-08','Grateful Dead','1977-05-08','Barton Hall, Cornell University','Ithaca','NY','https://www.gdao.org/items/show/10788',
 'A landmark Dead show with multiple independently documented circulating tape sources.',
 ['Jack Straw','Dancin’ in the Streets','Scarlet Begonias','Fire on the Mountain','Morning Dew'],'Cornell 1977', 'Multiple source versions exist for this single performance. Tape lineage is not a measure of objective audio quality.')
show('phish-1995-12-31','Phish','1995-12-31','Madison Square Garden','New York','NY','https://phish.net/setlists/phish-december-31-1995-madison-square-garden-new-york-ny-usa.html',
 'Three-set New Year’s Eve show, available as an official release.',
 ['Punch You in the Eye','Reba','Drowned','Mike’s Song','Weekapaug Groove','You Enjoy Myself'],'NYE 1995')
show('phish-2015-08-22','Phish','2015-08-22','Watkins Glen International','Watkins Glen','NY','https://phish.net/setlists/phish-august-22-2015-watkins-glen-international-watkins-glen-ny-usa.html',
 'Magnaball festival date notable for the Drive-In Jam.',
 ['Divided Sky',"Wolfman’s Brother",'Tweezer','Prince Caspian','Cities','Drive-In Jam'],'Magnaball')

# v0.8: additional editor-verified performance dates from official band show indexes.
# Empty song lists deliberately mean the linked source does not establish a setlist.
# Do not infer a recording from the presence of a show.
def documented(id, artist, date, venue, city, region, source, highlight, songs=None,
               slot='', notes=''):
    show(id, artist, date, venue, city, region, source, highlight, songs or [], slot, notes)
    row=H[-1]
    row['data_checked']='2026-10-28'
    row['setlist_scope']=('Selected songs supported by linked official show or release source; not a complete setlist'
                          if row['songs'] else 'Setlist not established by the cited source; no songs inferred')

# Original Duane-era performances: source links are individual event records.
documented('abb-1969-05-31',abb,'1969-05-31','Boston Tea Party','Boston','MA',
 'https://allmanbrothersband.com/event/abb19690531/',
 'Early Boston engagement. The official archive identifies the Velvet Underground on the bill.',
 notes='The official source documents a concert and billing, not a verified song list.')
documented('abb-1969-12-26-early',abb,'1969-12-26','Fillmore East','New York','NY',
 'https://allmanbrothersband.com/event/abb19691226/',
 'A first-year Fillmore East appearance, prior to the 1971 recording sessions.',
 slot='Early show', notes='Show time is estimated by the original archive; no songs inferred.')
documented('abb-1970-02-11-early',abb,'1970-02-11','Fillmore East','New York','NY',
 'https://allmanbrothersband.com/event/abb19700211/',
 'Early performance on a Fillmore East bill with the Grateful Dead and Love.',
 slot='Early show', notes='The source indexes early and late sets separately. Do not attribute an unidentified circulating tape to one without evidence.')
documented('abb-1970-04-04',abb,'1970-04-04','Ludlow Garage','Cincinnati','OH',
 'https://allmanbrothersband.com/event/abb19700404/',
 'The Cincinnati show associated with Live at Ludlow Garage 1970; the recording date has competing historical metadata.',
 ['Dreams','Statesboro Blues','Trouble No More','Dimples','Every Hungry Woman','Mountain Jam'],
 notes='DATE CAVEAT: official show index and several release catalogs favor April 4, 1970; some release metadata says April 11. Do not present the disputed release date as settled.')
documented('abb-1970-07-03',abb,'1970-07-03','Atlanta Pop Festival','Byron','GA',
 'https://allmanbrothersband.com/event/abb19700703/',
 'Atlanta International Pop Festival performance documented on the official two-disc live release.',
 ['Statesboro Blues','Trouble No More','Dreams','In Memory of Elizabeth Reed','Whipping Post','Mountain Jam'],
 notes='Selected titles cross-checked against the July 3 disc of the official Atlanta Pop release.')
documented('abb-1970-07-05',abb,'1970-07-05','Atlanta Pop Festival','Byron','GA',
 'https://allmanbrothersband.com/event/abb19700705/',
 'The second released Atlanta Pop set, commercially labeled July 5, with a post-midnight timing caveat.',
 ["Don’t Keep Me Wonderin’",'Statesboro Blues','In Memory of Elizabeth Reed','Stormy Monday','Whipping Post','Mountain Jam'],
 notes='DATE CAVEAT: official release markets this as July 5; its liner-note discussion places the actual set at about 3:50 a.m. July 6. Stored date follows original concert index and release label.')
documented('abb-1970-09-23',abb,'1970-09-23','Fillmore East','New York','NY',
 'https://allmanbrothersband.com/event/abb19700923/',
 'A return to the Fillmore East during the first full year of touring.',
 ["Don’t Keep Me Wonderin’",'Dreams','In Memory of Elizabeth Reed','Whipping Post'],
 notes='These selected songs are listed on the official band event record; surrounding bill notes are not songs.')
documented('abb-1971-03-11-early',abb,'1971-03-11','Fillmore East','New York','NY',
 'https://allmanbrothersband.com/event/abb19710311/',
 'A March Fillmore East show preceding the four performances represented in the definitive March 12–13 release.',
 slot='Early show',notes='Not to be conflated with the four March 12–13 performances on the official six-CD set.')
documented('abb-1971-06-25-early',abb,'1971-06-25','Fillmore East','New York','NY',
 'https://allmanbrothersband.com/event/abb19710625/',
 'An appearance during the venue’s final weekend, two days before the indexed June 27 closing set.',
 slot='Early show',notes='No source-verified setlist is attributed here.')
documented('abb-1971-10-17',abb,'1971-10-17','Painters Mill Music Fair','Owings Mills','MD',
 'https://allmanbrothersband.com/event/abb19711017/',
 'Duane Allman’s last concert, documented by the officially released audience cassette The Final Note.',
 ['Statesboro Blues','Trouble No More','One Way Out','In Memory of Elizabeth Reed','Whipping Post'],
 notes='The official release documents an audience cassette captured by Sam Idas; this is not a soundboard tape.')

# The Grateful Dead’s May 1977 tour: official dated show records, not tape assertions.
gd='Grateful Dead'
documented('gd-1977-05-05',gd,'1977-05-05','Veterans Memorial Coliseum','New Haven','CT',
 'https://www.dead.net/show/may-5-1977',
 'New Haven performance included in the official May 1977: Get Shown the Light collection.',
 ['Sugaree','Estimated Prophet','Scarlet Begonias','Fire on the Mountain','St. Stephen'])
documented('gd-1977-05-07',gd,'1977-05-07','Boston Garden','Boston','MA',
 'https://www.dead.net/show/may-7-1977',
 'Boston Garden performance recorded on Betty Cantor-Jackson’s soundboard source and issued in the official May 1977 box.',
 ['Bertha','Jack Straw','Terrapin Station','Eyes of the World','Wharf Rat'])
documented('gd-1977-05-09',gd,'1977-05-09','War Memorial Auditorium','Buffalo','NY',
 'https://www.dead.net/show/may-9-1977',
 'Buffalo show immediately following Cornell; all four dates May 5, 7, 8 and 9 appear on Get Shown the Light.',
 ['Help on the Way','Slipknot!','Franklin’s Tower','Estimated Prophet','Comes a Time'])
documented('gd-1977-05-11',gd,'1977-05-11','St. Paul Civic Center Arena','St. Paul','MN',
 'https://www.dead.net/show/may-11-1977',
 'A subsequent May 1977 tour stop documented by the Grateful Dead’s official show archive.',
 ['Promised Land','Sugaree','Scarlet Begonias','Fire on the Mountain','Brokedown Palace'])
documented('gd-1977-05-12',gd,'1977-05-12','Auditorium Theater','Chicago','IL',
 'https://www.dead.net/show/may-12-1977',
 'First of two indexed Auditorium Theater performances on May 12–13.',
 ['Bertha','Peggy-O','Terrapin Station','Not Fade Away','Comes a Time'])
documented('gd-1977-05-13',gd,'1977-05-13','Auditorium Theater','Chicago','IL',
 'https://www.dead.net/show/may-13-1977',
 'Second Chicago performance; the official source notes an FM broadcast and a Jack-a-Roe debut.',
 ['The Music Never Stopped','Jack-a-Roe','Scarlet Begonias','Fire on the Mountain','Stella Blue'])

R=[]
def recording(id,show_id,title,kind,url,provider,details,access='Link to external source'):
 R.append(dict(id=id,show_id=show_id,title=title,kind=kind,source_url=url,provider=provider,
  description=details,access=access,source_verified='page_link_checked_2026-10-26'))
abb_release='https://allmanbrothersband.com/discography/the-1971-fillmore-east-recordings/'
for sid,disc in [('abb-1971-03-12-late','Disc 2'),('abb-1971-03-13-early','Disc 3'),('abb-1971-03-13-late','Discs 4–5'),('abb-1971-06-27','Disc 6')]:
 recording('abb-1971-box-'+sid,sid,'The 1971 Fillmore East Recordings · '+disc,'Official archival release',abb_release,
 'The Allman Brothers Band official discography','An authorized commercial release; not freely downloadable from this site.')
recording('abb-final-2014','abb-2014-10-28','Final Concert 10-28-14','Official archival release',
 'https://allmanbrothersband.com/event/abb20141028/','Allman Brothers official archive',
 'The official show page links the 2014 final performance to an archival release.','Authorized commercial release link.')
recording('gd-cornell-1977-aud','gd-1977-05-08','Audience master source · Moore / Berger','Audience recording',
 'https://www.gdao.org/items/show/108289','Grateful Dead Archive Online',
 'Documents an audience tape source and its transfer notes.','External archival recording page; provider policies apply.')
recording('gd-cornell-1977-sbd','gd-1977-05-08','Betty Board source · soundboard / audience patches','Soundboard-derived recording',
 'https://www.gdao.org/items/show/332929','Grateful Dead Archive Online',
 'Soundboard-derived source with documented transfer and patches.','External archival recording page; provider policies apply.')
recording('gd-cornell-1977-mtx','gd-1977-05-08','Hunter’s Trix Vol. 40 · matrix','Matrix recording',
 'https://hunterstrix.com/releases/volume-40/','Hunter’s Trix',
 'A documented matrix combining soundboard and audience sources; linked page credits recordists and transfers.','External research/release page; provider policies apply.')
recording('phish-nye-1995','phish-1995-12-31','New Year’s Eve 1995','Official archival release',
 'https://www.livephish.com/LP-387.html','LivePhish',
 'Artist-authorized release of the December 31, 1995 MSG performance.','Subscription or purchase may be required.')

# v0.8 checked official release pointers, no album art, hosted media, or copying audio.
recording('abb-ludlow-1970-official','abb-1970-04-04','Live at Ludlow Garage 1970','Official archival release',
 'https://allmanbrothersband.com/discography/live-at-ludlow-garage-1970/','Allman Brothers official discography',
 'Official two-disc live release. Historical catalogs disagree on April 4 versus April 11; review the linked show and release information before citing the precise recording date.',
 'Commercial release information; no hosted audio.')
for sid, title in [('abb-1970-07-03','July 3 disc'), ('abb-1970-07-05','July 5 disc / after-midnight caveat')]:
 recording('abb-atlanta-pop-'+sid, sid, 'Live at the Atlanta International Pop Festival · '+title,
 'Official archival release',
 'https://allmanbrothersband.com/discography/the-allman-brothers-band-live-at-the-atlanta-intnl-pop-festival-july-3-5-1970/',
 'Allman Brothers official discography',
 'Disc documented by the official band discography. The July 5 billing has a post-midnight July 6 performance-time caveat.',
 'Commercial release information; no hosted audio.')
recording('abb-last-duane-show-1971','abb-1971-10-17','The Final Note: Painters Mill 10-17-71',
 'Official release from audience cassette',
 'https://allmanbrothersband.com/discography/the-final-note-painters-mill-music-fair-owings-mills-md-10-17-71/',
 'Allman Brothers official discography',
 'Contemporary handheld cassette recorded in the audience by Sam Idas; restored and officially released in 2020.',
 'Commercial release information; no hosted audio.')
for date in ['1977-05-05','1977-05-07','1977-05-09']:
 recording('gd-get-shown-the-light-'+date,'gd-'+date,
 'May 1977: Get Shown the Light · '+date,'Official archival box set',
 'https://www.rhino.com/article/pre-order-grateful-dead-may-1977-get-shown-the-light-and-cornell-5877',
 'Rhino Records / Grateful Dead',
 'Rhino identifies this performance as one of four complete shows in its 2017 official Betty Board-derived box set.',
 'Official commercial release information; availability may change.')
recording('gd-get-shown-the-light-cornell','gd-1977-05-08',
 'May 1977: Get Shown the Light · Cornell 5/8/77','Official archival box set',
 'https://www.rhino.com/article/pre-order-grateful-dead-may-1977-get-shown-the-light-and-cornell-5877',
 'Rhino Records / Grateful Dead',
 'Rhino documents the Cornell concert in this official Betty Board-based box, distinct from separately indexed audience tapes and matrix sources.',
 'Official commercial release information; availability may change.')

# Preserve the original nine v0.3 review dates. Date-stamp the eight v0.8
# manually cross-checked official release links with the actual review date.
for _row in R[9:]:
 _row['source_verified']='page_link_checked_2026-10-28'

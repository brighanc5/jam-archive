from pathlib import Path
p=Path(__file__).resolve().parent/'template.html'
s=p.read_text()
assert 'data-nav="history"' not in s
s=s.replace('<button data-nav="recordings">', '<button data-nav="history"><span><span class="icon">▤</span>Show history</span><em id="history-count">—</em></button>\n<button data-nav="recordings">',1)
s=s.replace('FOUNDING EDITION · v0.2','FOUNDING EDITION · v0.3').replace('JAM ARCHIVE · v0.2','JAM ARCHIVE · v0.3')
needle='<section class="view" id="view-recordings">'
assert needle in s
history='''<section class="view" id="view-history">
<div class="heading"><div><div class="eyebrow">The show laboratory / historical research</div><h2>Where the music happened</h2><p>Historic performances and their available sources, connected without confusing the show with the tape. This is a small <strong>curated research sample</strong>, not a complete archive.</p></div><span class="badge green">Original sources linked</span></div>
<div class="history-feature-row">
 <div class="history-feature"><div class="eyebrow">Follow the tapes</div><h3>One show. Three recordings.</h3><p>Cornell 1977: compare audience, soundboard-derived, and matrix sources for the same performance.</p><button id="history-tape-family" class="primary">Explore the tape family →</button></div>
 <div class="history-feature"><div class="eyebrow">The archive project</div><h3>Five Fillmore performances</h3><p>Trace the Allman Brothers' March 1971 early and late shows plus the June closing night.</p><button id="history-abb-run" class="outline">Explore the Fillmore run →</button></div>
 <div class="history-feature"><div class="eyebrow">Surprise me</div><h3>Take me to a show</h3><p>Discover a documented performance from our starter collection, then follow its original source.</p><button id="history-random" class="outline">Pick a show →</button></div>
</div>
<div class="twocol history-main-grid"><div>
 <div class="filterrow" style="margin-bottom:13px"><input class="field" id="history-search" type="search" placeholder="Search a song, year, venue, city…" aria-label="Search historical shows"><select class="bigselect" id="history-artist" aria-label="Filter archive by artist"></select></div>
 <div class="filterrow" style="margin-bottom:13px"><button class="pillbtn" id="history-recording-only">With recording pointers</button><button class="pillbtn" id="history-ny">New York shows</button><select class="bigselect" id="history-sort" aria-label="Sort shows" style="max-width:185px"><option value="new">Newest first</option><option value="old">Oldest first</option></select><span class="tiny" id="history-result-num"></span></div>
 <div id="history-results" class="history-stack"></div>
 </div>
 <div class="stack"><div class="card sidebarcard"><div class="eyebrow">Your Show Passport</div><h3>A living concert journal</h3><p>Mark nights you attended, listened to, or want to hear. Add private notes. Everything stays in this browser unless you export it.</p><div id="passport-counts" class="passport-stats"></div><div id="passport-list"></div><div class="filterrow"><button class="outline" id="passport-export">Export passport ↓</button><label class="outline history-import">Import JSON<input type="file" accept=".json,application/json" id="import-passport" hidden></label></div></div>
 <div class="card sidebarcard"><div class="eyebrow">New distinction</div><h3>One performance ≠ one tape</h3><p>A recording can be an audience tape, a soundboard transfer, a matrix, or an official release. Each has its own provenance and rights status. Our catalog preserves all of them separately.</p><p class="note">Links here do not authorize downloading, rebroadcasting or redistribution.</p></div>
 <div class="card sidebarcard"><div class="eyebrow">The song trail</div><h3>Follow a song into a show</h3><p>Search song titles across the <em>selected</em> setlist excerpts included here. Later, with licensed full setlists, this can become a real cross-artist song-history explorer.</p><div class="history-song-buttons"><button class="pillbtn" data-song="Whipping Post">Whipping Post</button><button class="pillbtn" data-song="Tweezer">Tweezer</button><button class="pillbtn" data-song="Morning Dew">Morning Dew</button></div></div></div></div>
</section>
'''
s=s.replace(needle,history+needle,1)
marker='</body></html>'
assert marker in s
modal='''<div id="history-dialog" class="modal" role="dialog" aria-modal="true" aria-label="Historical concert details"><div class="modalpanel history-dialog-panel"><div class="history-modal-toolbar"><span class="eyebrow">THE JAM ARCHIVE / SHOW DOSSIER</span><button class="close" id="close-history" aria-label="Close show details">×</button></div><div id="history-dialog-body"></div></div></div>
<script>\n'''
modal+=Path(__file__).with_name('history_ui.js').read_text()+'\n</script>\n'
s=s.replace(marker,modal+marker,1)
newcss='''\n/* v0.3 historical show dossier */
.history-feature-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:12px 0 28px}
.history-feature{background:linear-gradient(160deg,#1b2d2b,#111c20);border:1px solid var(--edge);border-radius:16px;padding:20px}
.history-feature:nth-child(2){background:linear-gradient(140deg,#25302a,#171c1b)}
.history-feature h3{margin:9px 0}.history-feature p{color:var(--muted);font-size:13px;min-height:70px}
.history-feature button{margin-top:5px}.history-main-grid{grid-template-columns:minmax(0,1.8fr) minmax(265px,1fr);gap:21px}
.history-stack{display:grid;gap:13px}.history-card{background:var(--panel);border:1px solid var(--edge);border-radius:14px;padding:19px}
.history-card:hover{border-color:#597c6c}.history-card-top{display:flex;justify-content:space-between;gap:15px}.history-card h3{margin:5px 0 0;font-size:20px}
.hist-link{border:0;background:transparent;color:var(--cream);padding:0;text-align:left;cursor:pointer;font-weight:650}
.hist-link:hover{text-decoration:underline;text-decoration-color:var(--lime)}.history-date{height:72px;min-width:68px;flex-shrink:0}
.history-desc{margin:16px 0 12px}.history-tags{display:flex;flex-wrap:wrap;gap:6px}.songline{color:var(--muted);font-size:12px;padding-top:13px}
.history-actions{margin-top:15px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}.history-detail-columns{margin:20px 0}
.history-import{display:inline-flex;align-items:center;cursor:pointer}.passport-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:17px 0}
.pass-stat{padding:9px;border:1px solid var(--edge);border-radius:9px;display:flex;flex-direction:column;gap:2px}
.pass-stat strong{font-size:22px;color:var(--lime)}.pass-stat span{font-size:10px;color:var(--muted)}
.history-song-buttons{display:flex;flex-wrap:wrap;gap:8px}.history-dialog-panel{max-width:940px}.history-modal-toolbar{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--edge);padding-bottom:13px;margin-bottom:22px}
.history-textarea{background:var(--panel2);color:var(--cream);border:1px solid var(--edge);border-radius:8px;width:100%;padding:10px;margin:7px 0 12px;resize:vertical;font:inherit}
.song-list{padding-left:23px}.song-list li{margin:5px 0}.tape-entry{display:grid;grid-template-columns:46px 1fr;gap:14px;padding:20px 0;border-bottom:1px solid var(--edge)}
.tape-entry h3{margin:7px 0}.tape-entry p{margin:5px 0}.tape-icon{font-size:26px;color:var(--lime)}
@media(max-width:900px){.history-feature-row{grid-template-columns:1fr}.history-feature p{min-height:auto}.history-main-grid{grid-template-columns:1fr}}
@media(max-width:500px){.history-card h3{font-size:17px}.history-date{display:none}}
'''
s=s.replace('</style>',newcss+'\n</style>',1)
p.write_text(s)
print('Updated template',len(s))

/* v0.7 Recording Explorer: public editorial metadata only, no audio or tracking. */
(()=>{'use strict';
const search=document.getElementById('recording-search');
const artist=document.getElementById('recording-artist');
const kind=document.getElementById('recording-kind');
const sort=document.getElementById('recording-sort');
const results=document.getElementById('recording-results');
const counter=document.getElementById('recording-count');
let records=[];const batch=matchMedia('(max-width:760px)').matches?10:18;let limit=batch;
const pager=document.createElement('div');pager.className='ja-pager';const more=document.createElement('button');more.type='button';more.className='ja-load-more';more.textContent='More tape sources';pager.append(more);results.after(pager);
const el=(tag,cl,text)=>{const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=text;return x;};
const append=(parent,...children)=>{children.forEach(x=>parent.appendChild(x));return parent;};
function card(r){
 const c=el('article','recording-card');
 append(c,el('div','topline',r.kind),el('h3','',r.title));
 append(c,el('div','show-meta',`${r.artist} · ${r.date}${r.slot?' · '+r.slot:''}`),el('div','show-meta',`${r.venue} · ${r.city}, ${r.region}`));
 append(c,el('p','desc',r.description));
 const actions=el('div','actions');
 const out=el('a','', 'Original source ↗');out.href=r.source_url;out.target='_blank';out.rel='noopener noreferrer';
 const show=el('a','', 'Concert dossier →');show.href=r.show_url;
 append(actions,out,show);append(c,actions,el('div','source-note',`${r.provider} · ${r.access}`));
 return c;
}
function render(){
 const q=search.value.toLocaleLowerCase().trim();
 const found=records.filter(r=>(!artist.value||r.artist===artist.value)&&(!kind.value||r.kind===kind.value)&&(!q||[r.title,r.artist,r.venue,r.city,r.date,r.kind,r.provider,r.description].join(' ').toLocaleLowerCase().includes(q)));
 found.sort((a,b)=>sort.value==='title'?a.title.localeCompare(b.title):sort.value==='newest'?b.date.localeCompare(a.date)||a.title.localeCompare(b.title):a.date.localeCompare(b.date)||a.title.localeCompare(b.title));
 results.replaceChildren(...found.slice(0,limit).map(card));
 more.hidden=limit>=found.length;
 if(!found.length)results.appendChild(el('p','no-results','No matching source references in this limited curated collection. Try another search or contribute a missing tape.'));
 counter.textContent=`Showing ${Math.min(limit,found.length)} of ${found.length} matching recording sources`;
}
for(const field of [search,artist,kind,sort])field.addEventListener(field===search?'input':'change',()=>{limit=batch;render()});
more.addEventListener('click',()=>{limit+=batch;render()});
fetch('../assets/recordings.json').then(res=>{if(!res.ok)throw Error('Index request failed');return res.json();}).then(doc=>{
 if(doc.version!==1||!Array.isArray(doc.items))throw Error('Unknown source index format');
 records=doc.items;
 [...new Set(records.map(r=>r.kind))].sort().forEach(k=>{const opt=el('option','',k);opt.value=k;kind.appendChild(opt)});
 render();
}).catch(()=>{counter.textContent='Index temporarily unavailable';results.replaceChildren(el('p','no-results','Unable to load recording references. Please refresh the page.'));});
})();

/* Static, progressive-enhancement directory: all 53 entries exist in HTML without JS. */
(()=>{'use strict';
const search=document.querySelector('#sp-search');
const artist=document.querySelector('#sp-artist');
const sort=document.querySelector('#sp-sort');
const repeats=document.querySelector('#sp-repeats');
const grid=document.querySelector('#sp-grid');
const count=document.querySelector('#sp-count');
const empty=document.querySelector('#sp-empty');
if(!search||!artist||!sort||!repeats||!grid||!count||!empty)return;
const cards=[...grid.querySelectorAll('.sp-card')];
function update(){
 const term=search.value.trim().toLocaleLowerCase();let showing=0;
 for(const card of cards){
  const match=(!term||card.textContent.toLocaleLowerCase().includes(term))&&
   (!artist.value||card.dataset.artists.split('|').includes(artist.value))&&
   (!repeats.checked||Number(card.dataset.count)>1);
  card.hidden=!match;if(match)showing++;
 }
 const sorted=[...cards].sort((a,b)=>sort.value==='alpha'?
  a.dataset.song.localeCompare(b.dataset.song):
  Number(b.dataset.count)-Number(a.dataset.count)||a.dataset.song.localeCompare(b.dataset.song));
 for(const card of sorted)grid.appendChild(card);
 count.textContent=`Showing ${showing} of ${cards.length} indexed song titles`;
 empty.hidden=showing!==0;
}
[search,artist,sort].forEach(el=>el.addEventListener(el===search?'input':'change',update));
repeats.addEventListener('change',update);update();
})();

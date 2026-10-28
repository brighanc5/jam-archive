/* The Jam Archive v0.8 — progressive-enhancement filters; full content exists in HTML. */
(()=>{'use strict';
const search=document.querySelector('#tm-search'),artist=document.querySelector('#tm-artist');
const year=document.querySelector('#tm-year'),recorded=document.querySelector('#tm-recorded');
const count=document.querySelector('#tm-results'),empty=document.querySelector('#tm-empty');
const items=[...document.querySelectorAll('.tm-show')];
const groups=[...document.querySelectorAll('.tm-year-group')];
function update(){
 const term=search.value.trim().toLocaleLowerCase();let visible=0;
 for(const item of items){
  const match=(!term||item.textContent.toLocaleLowerCase().includes(term))&&
    (!artist.value||item.dataset.artist===artist.value)&&
    (!year.value||item.dataset.year===year.value)&&
    (!recorded.checked||item.dataset.sources!=='0');
  item.hidden=!match;if(match)visible++;
 }
 for(const group of groups)group.hidden=![...group.querySelectorAll('.tm-show')].some(x=>!x.hidden);
 count.textContent=`Showing ${visible} of ${items.length} source-linked performances`;
 empty.hidden=visible!==0;
}
[search,artist,year].forEach(el=>el.addEventListener(el===search?'input':'change',update));
recorded.addEventListener('change',update);update();
})();

/* All titles remain server-rendered; JS filters, sorts, and progressively reveals. */
(()=>{'use strict';
const search=document.querySelector('#sp-search'),artist=document.querySelector('#sp-artist'),sort=document.querySelector('#sp-sort'),repeats=document.querySelector('#sp-repeats'),grid=document.querySelector('#sp-grid'),count=document.querySelector('#sp-count'),empty=document.querySelector('#sp-empty');
if(!search||!artist||!sort||!repeats||!grid||!count||!empty)return;
const cards=[...grid.querySelectorAll('.sp-card')],batch=matchMedia('(max-width:760px)').matches?16:28;let limit=batch;
const pager=document.createElement('div');pager.className='ja-pager';const more=document.createElement('button');more.type='button';more.className='ja-load-more';more.textContent='More song titles';const note=document.createElement('span');note.className='ja-pager-note';pager.append(more,note);grid.after(pager);
function update(){
 const term=search.value.trim().toLocaleLowerCase();let total=0,shown=0;
 const sorted=[...cards].sort((a,b)=>sort.value==='alpha'?a.dataset.song.localeCompare(b.dataset.song):Number(b.dataset.count)-Number(a.dataset.count)||a.dataset.song.localeCompare(b.dataset.song));
 for(const card of sorted){const match=(!term||card.textContent.toLocaleLowerCase().includes(term))&&(!artist.value||card.dataset.artists.split('|').includes(artist.value))&&(!repeats.checked||Number(card.dataset.count)>1);if(match){total++;if(total<=limit)shown++;}card.hidden=!match||total>limit;grid.appendChild(card)}
 count.textContent=`Showing ${shown} of ${total} matching tunes (${cards.length} indexed)`;empty.hidden=total!==0;more.hidden=shown>=total;note.textContent=total>shown?`${total-shown} more in the crate`:'End of this stack';
}
for(const el of [search,artist,sort,repeats])el.addEventListener(el===search?'input':'change',()=>{limit=batch;update()});more.addEventListener('click',()=>{limit+=batch;update()});update();
})();

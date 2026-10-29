/* Timeline: no-JS shows all; filtering and paging only enhance the experience. */
(()=>{'use strict';
 const search=document.querySelector('#tm-search'),artist=document.querySelector('#tm-artist'),year=document.querySelector('#tm-year'),recorded=document.querySelector('#tm-recorded'),count=document.querySelector('#tm-results'),empty=document.querySelector('#tm-empty');
 if(!search||!artist||!year||!recorded||!count||!empty)return;
 const items=[...document.querySelectorAll('.tm-show')],groups=[...document.querySelectorAll('.tm-year-group')],batch=matchMedia('(max-width:760px)').matches?10:18;let limit=batch;
 const pager=document.createElement('div');pager.className='ja-pager';const more=document.createElement('button');more.type='button';more.className='ja-load-more';more.textContent='More shows';pager.append(more);groups[groups.length-1]?.after(pager);
 function update(){const term=search.value.trim().toLocaleLowerCase();let found=0,shown=0;
  for(const item of items){const match=(!term||item.textContent.toLocaleLowerCase().includes(term))&&(!artist.value||item.dataset.artist===artist.value)&&(!year.value||item.dataset.year===year.value)&&(!recorded.checked||item.dataset.sources!=='0');if(match){found++;if(found<=limit)shown++;}item.hidden=!match||found>limit;}
  for(const group of groups)group.hidden=![...group.querySelectorAll('.tm-show')].some(x=>!x.hidden);
  count.textContent=`Showing ${shown} of ${found} matching shows`;empty.hidden=found!==0;more.hidden=shown>=found;
 }
 for(const el of [search,artist,year,recorded])el.addEventListener(el===search?'input':'change',()=>{limit=batch;update()});more.addEventListener('click',()=>{limit+=batch;update()});update();
})();

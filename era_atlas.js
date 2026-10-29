/* Atlas: all 361 records exist in the HTML. JavaScript adds filters and paging. */
(()=>{'use strict';
 const q=document.getElementById('ea-search'),artist=document.getElementById('ea-artist'),year=document.getElementById('ea-year'),kind=document.getElementById('ea-kind'),status=document.getElementById('ea-results');
 if(!q||!artist||!year||!kind||!status)return;
 const cards=[...document.querySelectorAll('.ea-card[data-artist]')];
 const pageSize=matchMedia('(max-width: 760px)').matches?18:36;
 let limit=pageSize;
 const pager=document.createElement('div');pager.className='ja-pager';
 const more=document.createElement('button');more.type='button';more.className='ja-load-more';more.textContent='Show more gigs';more.setAttribute('aria-controls','ea-list');
 const note=document.createElement('span');note.className='ja-pager-note';pager.append(more,note);
 const grid=cards[0]?.parentElement;if(grid){grid.id=grid.id||'ea-list';grid.after(pager)}
 function render(){let total=0,shown=0;const term=q.value.trim().toLocaleLowerCase();
  for(const c of cards){const found=(!term||(c.dataset.search||'').includes(term))&&(!artist.value||c.dataset.artist===artist.value)&&(!year.value||c.dataset.year===year.value)&&(!kind.value||c.dataset.kind===kind.value);if(found){total++;if(total<=limit)shown++;}c.hidden=!found||total>limit;}
  status.textContent=`Showing ${shown} of ${total} matching shows`;note.textContent=total>shown?`${total-shown} more to explore`:'You’re all caught up on this list';more.hidden=shown>=total;
 }
 for(const el of [q,artist,year,kind])el.addEventListener(el===q?'input':'change',()=>{limit=pageSize;render()});
 more.addEventListener('click',()=>{limit+=pageSize;render()});
 const p=new URLSearchParams(location.search);if(p.has('artist'))artist.value=p.get('artist');if(p.has('q'))q.value=p.get('q');render();
})();

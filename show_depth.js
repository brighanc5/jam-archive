/* Show Studies and Repertoire: browse every match, one manageable batch at a time. */
(()=>{'use strict';
 const search=document.getElementById('sd-search'),artist=document.getElementById('sd-artist'),status=document.getElementById('sd-count');
 if(!search||!status)return;
 const cards=[...document.querySelectorAll('[data-depth-record]')];const batch=matchMedia('(max-width: 760px)').matches?16:28;let limit=batch;
 const grid=cards[0]?.parentElement;const pager=document.createElement('div');pager.className='ja-pager';
 const more=document.createElement('button');more.className='ja-load-more';more.type='button';more.textContent='Keep digging';
 const note=document.createElement('span');note.className='ja-pager-note';pager.append(more,note);if(grid)grid.after(pager);
 const params=new URLSearchParams(location.search);if(params.get('q'))search.value=params.get('q');if(artist&&params.get('artist'))artist.value=params.get('artist');
 function update(){let found=0,shown=0;const q=search.value.trim().toLocaleLowerCase();
  for(const card of cards){const match=(!artist||!artist.value||card.dataset.artist===artist.value)&&(!q||(card.dataset.search||'').includes(q));if(match){found++;if(found<=limit)shown++;}card.hidden=!match||found>limit;}
  status.textContent=`Showing ${shown} of ${found} matches`;more.hidden=shown>=found;note.textContent=found>shown?`${found-shown} more to check out`:'End of the list';
 }
 search.addEventListener('input',()=>{limit=batch;update()});if(artist)artist.addEventListener('change',()=>{limit=batch;update()});more.addEventListener('click',()=>{limit+=batch;update()});update();
})();

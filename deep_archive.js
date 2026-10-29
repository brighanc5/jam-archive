/* Research library: full HTML works without scripts; paging is optional. */
document.addEventListener('DOMContentLoaded',()=>{
 const search=document.getElementById('da-query'),filter=document.getElementById('da-filter'),tiles=[...document.querySelectorAll('.da-tile[data-search]')],count=document.getElementById('da-match-count');
 if(!search||!filter||!count||!tiles.length)return;
 const batch=matchMedia('(max-width:760px)').matches?12:20;let limit=batch;
 const pager=document.createElement('div');pager.className='ja-pager';const more=document.createElement('button');more.type='button';more.className='ja-load-more';more.textContent='More stories';pager.append(more);tiles[tiles.length-1].parentElement.after(pager);
 function update(){const q=search.value.toLocaleLowerCase().trim(),f=filter.value;let found=0,shown=0;for(const tile of tiles){const match=(!q||tile.dataset.search.includes(q))&&(f==='all'||tile.dataset.kind===f);if(match){found++;if(found<=limit)shown++;}tile.hidden=!match||found>limit;}count.textContent=`Showing ${shown} of ${found} stories`;more.hidden=shown>=found;}
 search.addEventListener('input',()=>{limit=batch;update()});filter.addEventListener('change',()=>{limit=batch;update()});more.addEventListener('click',()=>{limit+=batch;update()});update();
});

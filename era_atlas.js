(()=>{'use strict';
  const q=document.getElementById('ea-search'),artist=document.getElementById('ea-artist'),year=document.getElementById('ea-year'),kind=document.getElementById('ea-kind'),count=document.getElementById('ea-results');
  if(!q||!artist||!year||!kind||!count)return;
  const cards=[...document.querySelectorAll('.ea-card[data-artist]')];
  function render(){let n=0;const term=q.value.trim().toLocaleLowerCase();for(const c of cards){const found=(!term||c.dataset.search.includes(term))&&(!artist.value||c.dataset.artist===artist.value)&&(!year.value||c.dataset.year===year.value)&&(!kind.value||c.dataset.kind===kind.value);c.hidden=!found;if(found)n++;}count.textContent=n+' indexed performances match your filters.';}
  for(const el of [q,artist,year,kind])el.addEventListener(el===q?'input':'change',render);
  const p=new URLSearchParams(location.search);if(p.has('artist'))artist.value=p.get('artist');if(p.has('q'))q.value=p.get('q');render();
})();

'use strict';
(function(){
  const query=document.getElementById('pl-search');
  const artist=document.getElementById('pl-artist');
  const cards=[...document.querySelectorAll('.pl-card')];
  const count=document.getElementById('pl-count');
  if(!query||!artist||!count)return;
  function filter(){
    const q=query.value.trim().toLocaleLowerCase();
    const a=artist.value;
    let n=0;
    for(const card of cards){
      const show=(a===''||card.dataset.artist===a)&&(!q||card.dataset.search.includes(q));
      card.hidden=!show;
      if(show)n++;
    }
    count.textContent=n+' of '+cards.length+' evidence studies shown';
  }
  query.addEventListener('input',filter);
  artist.addEventListener('change',filter);
})();

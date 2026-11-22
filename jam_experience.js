/* The Jam Archive: lightweight, dependency-free mobile navigation. */
(()=>{'use strict';
 const root=document.body;
 if(!root)return;
 const routes=[['⌕','Find','/#discover'],['◈','Shows','/era-atlas/'],['♫','Songs','/repertoire/'],['✦','People','/connections/'],['◎','Dig in','/show-depth/']];
 const nav=document.createElement('nav');nav.className='ja-mobile-bar';nav.setAttribute('aria-label','Quick navigation');
 const path=location.pathname;
 for(const [symbol,label,url] of routes){const a=document.createElement('a');a.href=url;
  const graphic=document.createElement('span');graphic.textContent=symbol;graphic.setAttribute('aria-hidden','true');
  const caption=document.createElement('span');caption.textContent=label;a.append(graphic,caption);
  if((url==='/#discover'&&path==='/')||path===url||(url==='/show-depth/'&&path.startsWith('/show-depth/'))||(url==='/repertoire/'&&path.startsWith('/repertoire/'))||(url==='/era-atlas/'&&path.startsWith('/era-atlas/'))||(url==='/connections/'&&path.startsWith('/connections/')))a.setAttribute('aria-current','page');
  nav.append(a);
 }
 root.append(nav);
 // Keep the dedicated Find tab useful even when clicking it on the homepage.
 if(location.pathname==='/'){
  const openSearch=()=>{if(location.hash==='#discover')document.querySelector('[data-nav="discover"]')?.click()};
  window.addEventListener('hashchange',openSearch);openSearch();
 }
})();
/* Upcoming shows: hide dates that have passed (pages stay static; see scripts/build_upcoming.py). */
(()=>{'use strict';
 const today=new Date().toLocaleDateString('en-CA');
 const past=el=>(el.dataset.showEnd||el.dataset.showDate)<today;
 const show=document.querySelector('article.ja-show[data-show-date]');
 if(show&&past(show)){
  show.querySelector('.ja-ticket-box')?.setAttribute('hidden','');
  show.querySelector('.ja-prices')?.setAttribute('hidden','');
  show.querySelector('.ja-past-note')?.removeAttribute('hidden');
 }
 // Stored prices expire: never leave an old snapshot looking current (see upcoming_shows.MAX_QUOTE_AGE).
 const prices=show?.querySelector('.ja-prices[data-fresh-until]');
 if(prices){const until=Date.parse(prices.dataset.freshUntil);
  if(!(until>Date.now())){prices.hidden=true;show.querySelector('.ja-price-note')?.removeAttribute('hidden')}}
 for(const el of document.querySelectorAll('li[data-show-date],.item[data-show-date]'))if(past(el))el.hidden=true;
 const lists=[...document.querySelectorAll('[data-show-list]')];
 let any=false;
 for(const list of lists){
  const left=[...list.querySelectorAll('[data-show-date]')].some(el=>!el.hidden);
  any=any||left;
  const none=list.querySelector('.ja-none-left');
  if(none)none.hidden=left;
  else if(!left&&list.tagName==='SECTION'&&!list.classList.contains('card'))list.hidden=true;
 }
 if(location.pathname==='/upcoming/'){const n=document.querySelector('main>.ja-none-left');if(n)n.hidden=any}
})();

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

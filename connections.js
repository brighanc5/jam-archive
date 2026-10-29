/* The Jam Archive v0.10: entirely local, source-verified relationship explorer. */
(() => {
  'use strict';
  const payload = document.querySelector('#cx-data');
  if (!payload) return;
  let data;
  try { data = JSON.parse(payload.textContent); } catch (_) { return; }
  const byId = new Map(data.nodes.map(n => [n.id, n]));
  const adjacency = new Map(data.nodes.map(n => [n.id, []]));
  for (const edge of data.edges) {
    if (adjacency.has(edge.from) && adjacency.has(edge.to)) {
      adjacency.get(edge.from).push({ id: edge.to, edge });
      adjacency.get(edge.to).push({ id: edge.from, edge });
    }
  }
  const get = id => document.getElementById(id);
  const focusInput = get('cx-focus');
  const fromInput = get('cx-from');
  const toInput = get('cx-to');
  const network = get('cx-network');
  const pathArea = get('cx-path');
  const ns = 'http://www.w3.org/2000/svg';
  const name = id => byId.get(id)?.name ?? id;
  const make = (tag, cls, text) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const svg = (tag, attrs, text) => {
    const el = document.createElementNS(ns, tag);
    for (const [k,v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const link = (url, title, cls='') => {
    const el = make('a', cls, title);
    el.href = url;
    return el;
  };
  const relation = (edge, a, b) => {
    if (edge.type === 'member_of') return a === edge.from ? 'Documented member of' : 'Documented project member';
    return 'Documented collaboration';
  };
  function setFocus(id) {
    if (!byId.has(id)) return;
    focusInput.value = id;
    const center = byId.get(id);
    const neighbors = [...adjacency.get(id)].sort((a,b) => name(a.id).localeCompare(name(b.id)));
    get('cx-focus-title').textContent = center.name;
    get('cx-focus-note').textContent = neighbors.length + ' directly source-verified ' + (neighbors.length === 1 ? 'relationship' : 'relationships') + '. Select a node to refocus.';
    get('cx-profile').href = '../artists/' + encodeURIComponent(id) + '/index.html';
    const neighborList = get('cx-neighbors');
    neighborList.replaceChildren();
    for (const {id: other, edge} of neighbors) {
      const li = make('li');
      const button = make('button', 'cx-neighbor-button', name(other));
      button.type = 'button';
      button.addEventListener('click', () => setFocus(other));
      li.append(button, make('span', 'cx-edge-kind', relation(edge, id, other)));
      if (edge.note) li.append(make('span', 'cx-edge-kind', edge.note));
      const cited = link(edge.source_url, 'View evidence ↗', 'cx-source');
      cited.target = '_blank'; cited.rel = 'noopener noreferrer';
      li.append(cited); neighborList.append(li);
    }
    network.replaceChildren();
    const cx = 380, cy = 235;
    const count = neighbors.length;
    const radiusX = count > 5 ? 292 : 260;
    const radiusY = count > 5 ? 173 : 151;
    const positions = neighbors.map((n, i) => {
      const t = (2 * Math.PI * i) / Math.max(1, count) - Math.PI / 2;
      return { x: cx + Math.cos(t) * radiusX, y: cy + Math.sin(t) * radiusY };
    });
    for (const pos of positions) network.append(svg('line', {x1:cx,y1:cy,x2:pos.x,y2:pos.y,class:'cx-line'}));
    const central = svg('g', {'class':'cx-svg-center'});
    central.append(svg('circle',{cx,cy,r:70}), svg('text',{x:cx,y:cy,'text-anchor':'middle',y:cy-7},center.name.length > 23 ? center.name.slice(0,22) + '…' : center.name));
    central.append(svg('text',{x:cx,y:cy+17,'text-anchor':'middle',class:'cx-svg-sub'},'FOCUS'));
    network.append(central);
    for (let i=0;i<count;i++) {
      const other = neighbors[i].id;
      const pos = positions[i];
      const n = svg('g', {'class':'cx-svg-node',tabindex:'0',role:'button','aria-label':'Focus on '+name(other)});
      n.append(svg('circle',{cx:pos.x,cy:pos.y,r:48}));
      const label = name(other);
      const words = label.split(' ');
      let first = label, second = '';
      if (label.length > 16) {
        const cut = Math.max(1, Math.floor(words.length/2));
        first = words.slice(0,cut).join(' ');
        second = words.slice(cut).join(' ');
      }
      if (first.length > 16) first = first.slice(0,15)+'…';
      if (second.length > 16) second = second.slice(0,15)+'…';
      n.append(svg('text',{x:pos.x,y:pos.y + (second ? -6 : 4),'text-anchor':'middle'},first));
      if (second) n.append(svg('text',{x:pos.x,y:pos.y+10,'text-anchor':'middle'},second));
      n.addEventListener('click', () => setFocus(other));
      n.addEventListener('keydown', ev => {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); setFocus(other); }
      });
      network.append(n);
    }
    const selectedUrl = new URL(window.location.href);
    selectedUrl.searchParams.set('artist', id);
    window.history.replaceState(null, '', selectedUrl.pathname + selectedUrl.search + selectedUrl.hash);
  }
  function shortest(start, end) {
    if (start === end) return [start];
    if (!byId.has(start) || !byId.has(end)) return null;
    const prev = new Map([[start,null]]);
    const q = [start];
    for (let i=0;i<q.length;i++) {
      const current = q[i];
      for (const {id: next} of adjacency.get(current)) {
        if (prev.has(next)) continue;
        prev.set(next,current);
        if (next === end) {
          const out = [end];
          while (prev.get(out[0]) !== null) out.unshift(prev.get(out[0]));
          return out;
        }
        q.push(next);
      }
    }
    return null;
  }
  function showPath() {
    const start = fromInput.value, end = toInput.value;
    pathArea.replaceChildren();
    if (!byId.has(start) || !byId.has(end)) return;
    const path = shortest(start,end);
    if (!path) {
      pathArea.append(make('h3',null,'No reviewed path in this catalog—yet.'),
        make('p',null,name(start)+' and '+name(end)+' are in different verified network groups. This is a research gap, not evidence that the musicians never played together.'));
      return;
    }
    if (path.length === 1) {
      pathArea.append(make('p',null,'You selected the same entry twice. Choose another to discover a path.'));
      return;
    }
    pathArea.append(make('h3',null,(path.length-1)+' verified ' + ((path.length-1)===1?'link':'links')+' connect '+name(start)+' and '+name(end)+'.'));
    const ol = make('ol','cx-route');
    for(let i=0;i<path.length-1;i++) {
      const a=path[i],b=path[i+1];
      const found=adjacency.get(a).find(x=>x.id===b);
      const step=make('li');
      step.append(link('../artists/'+encodeURIComponent(a)+'/index.html',name(a)));
      step.append(make('span','cx-route-arrow',' → '+relation(found.edge,a,b)+' → '));
      step.append(link('../artists/'+encodeURIComponent(b)+'/index.html',name(b)));
      const source=link(found.edge.source_url,'Source ↗','cx-source');
      source.target='_blank';source.rel='noopener noreferrer';
      step.append(source);
      if(found.edge.note) step.append(make('p','cx-small',found.edge.note));
      ol.append(step);
    }
    pathArea.append(ol);
    pathArea.append(make('p','cx-small','Paths are chains of independently verified relationships—not proof of a shared stage or timeline.'));
  }
  focusInput.addEventListener('change', () => setFocus(focusInput.value));
  get('cx-find').addEventListener('click',showPath);
  document.querySelectorAll('.cx-example').forEach(button => button.addEventListener('click', () => {
    fromInput.value = button.dataset.start;toInput.value = button.dataset.end;showPath();
    pathArea.scrollIntoView({behavior:'smooth',block:'nearest'});
  }));
  const search = get('cx-ledger-search');
  const ledger = [...document.querySelectorAll('.cx-ledger-item')];
  search.addEventListener('input', () => {
    const term=search.value.trim().toLocaleLowerCase();let visible=0;
    for(const li of ledger) { li.hidden=!!term&&!li.dataset.names.includes(term);if(!li.hidden) visible++; }
    get('cx-ledger-count').textContent=visible+' of '+ledger.length+' verified relationships';
  });
  const requested = new URLSearchParams(window.location.search).get('artist');
  setFocus(byId.has(requested) ? requested : 'trey-anastasio');
  fromInput.value = 'trey-anastasio';
  toInput.value = 'les-claypool';
  showPath();
})();

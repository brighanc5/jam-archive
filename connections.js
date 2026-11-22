/* The Jam Archive Family Tree: local, source-verified relationship explorer. No network calls. */
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
  const map = get('cx-map');
  const mapNodes = map ? new Map([...map.querySelectorAll('.cx-map-node')].map(n => [n.dataset.id, n])) : new Map();
  const mapEdges = map ? [...map.querySelectorAll('.cx-map-edge')] : [];
  function highlightOnMap(path) {
    if (!map) return;
    const onPath = new Set(path || []);
    const pairs = new Set();
    for (let i = 0; path && i < path.length - 1; i++) { pairs.add(path[i] + '|' + path[i+1]); pairs.add(path[i+1] + '|' + path[i]); }
    map.classList.toggle('has-path', !!(path && path.length > 1));
    map.querySelectorAll('.cx-map-tmp').forEach(t => t.remove());
    for (const [id, node] of mapNodes) {
      const on = onPath.has(id);
      node.classList.toggle('on-path', on);
      if (on && !node.querySelector('text')) {
        const c = node.querySelector('circle');
        node.append(svg('text', {x: c.getAttribute('cx'), y: Number(c.getAttribute('cy')) - Number(c.getAttribute('r')) - 4, 'text-anchor': 'middle', 'class': 'cx-map-tmp'}, name(id)));
      }
    }
    for (const line of mapEdges) line.classList.toggle('on-path', pairs.has(line.dataset.a + '|' + line.dataset.b));
    const wrap = map.parentElement;
    if (path && path.length && wrap.scrollWidth > wrap.clientWidth) {
      const xs = path.map(id => Number(mapNodes.get(id)?.querySelector('circle').getAttribute('cx') || 500));
      const mid = (Math.min(...xs) + Math.max(...xs)) / 2 / 1000 * wrap.scrollWidth;
      wrap.scrollLeft = Math.max(0, mid - wrap.clientWidth / 2);
    }
  }
  const verb = (edge, a) => {
    if (edge.type !== 'member_of') return 'collaborated with';
    return a === edge.from ? 'was in' : 'included';
  };
  const chainNode = id => {
    const n = byId.get(id);
    const a = link('../artists/' + encodeURIComponent(id) + '/index.html', n.name, 'cx-chain-node cx-chain-' + (n.type === 'person' ? 'person' : 'band'));
    return a;
  };
  function shareUrl() {
    const url = new URL(window.location.href);
    url.search = ''; url.hash = '';
    url.searchParams.set('from', fromInput.value); url.searchParams.set('to', toInput.value);
    return url;
  }
  function showPath() {
    const start = fromInput.value, end = toInput.value;
    pathArea.replaceChildren();
    get('cx-share').hidden = true; get('cx-share-status').textContent = '';
    highlightOnMap(null);
    if (!byId.has(start) || !byId.has(end)) return;
    const path = shortest(start,end);
    if (!path) {
      pathArea.append(make('h3',null,'No sourced path yet.'),
        make('p',null,name(start)+' and '+name(end)+' are in different verified network groups. This is a research gap, not evidence that the musicians never played together.'));
      return;
    }
    if (path.length === 1) {
      pathArea.append(make('p',null,'Same name twice. Pick someone else to connect.'));
      return;
    }
    const hops = path.length - 1;
    const head = make('h3', 'cx-path-title');
    head.append(make('span', null, name(start) + ' → ' + name(end)), make('span', 'cx-hops', hops + (hops === 1 ? ' link' : ' links')));
    const chain = make('ol', 'cx-chain');
    for (let i = 0; i < path.length; i++) {
      const li = make('li', 'cx-chain-step');
      li.append(chainNode(path[i]));
      if (i < path.length - 1) {
        const a = path[i], b = path[i+1];
        const found = adjacency.get(a).find(x => x.id === b);
        const rel = make('div', 'cx-chain-rel');
        rel.append(make('span', 'cx-chain-verb', verb(found.edge, a)));
        if (found.edge.note) rel.append(make('span', 'cx-chain-note', found.edge.note));
        const source = link(found.edge.source_url, 'source ↗', 'cx-source');
        source.target = '_blank'; source.rel = 'noopener noreferrer';
        rel.append(source);
        li.append(rel);
      }
      chain.append(li);
    }
    pathArea.append(head, chain);
    get('cx-share').hidden = false;
    highlightOnMap(path);
    const url = shareUrl();
    window.history.replaceState(null, '', url.pathname + url.search);
  }
  focusInput.addEventListener('change', () => setFocus(focusInput.value));
  get('cx-find').addEventListener('click', showPath);
  get('cx-swap').addEventListener('click', () => { const t = fromInput.value; fromInput.value = toInput.value; toInput.value = t; showPath(); });
  const mainWeb = data.nodes.filter(n => n.component === 0).map(n => n.id);
  get('cx-random').addEventListener('click', () => {
    // Pick two names in the main web that are at least three links apart.
    for (let tries = 0; tries < 60; tries++) {
      const a = mainWeb[Math.floor(Math.random() * mainWeb.length)], b = mainWeb[Math.floor(Math.random() * mainWeb.length)];
      const p = shortest(a, b);
      if (p && p.length >= 4) { fromInput.value = a; toInput.value = b; break; }
    }
    showPath();
  });
  get('cx-share').addEventListener('click', async () => {
    const status = get('cx-share-status');
    const url = shareUrl().toString();
    try { await navigator.clipboard.writeText(url); status.textContent = 'Link copied.'; }
    catch (_) { status.textContent = url; }
  });
  document.querySelectorAll('.cx-example').forEach(button => button.addEventListener('click', () => {
    fromInput.value = button.dataset.start; toInput.value = button.dataset.end; showPath();
    pathArea.scrollIntoView({behavior:'smooth',block:'nearest'});
  }));
  for (const [id, node] of mapNodes) {
    node.addEventListener('click', ev => {
      ev.preventDefault();
      setFocus(id);
      get('cx-focus-panel').scrollIntoView({behavior:'smooth', block:'start'});
    });
  }
  const search = get('cx-ledger-search');
  const ledger = [...document.querySelectorAll('.cx-ledger-item')];
  search.addEventListener('input', () => {
    const term=search.value.trim().toLocaleLowerCase();let visible=0;
    for(const li of ledger) { li.hidden=!!term&&!li.dataset.names.includes(term);if(!li.hidden) visible++; }
    get('cx-ledger-count').textContent=visible+' of '+ledger.length+' verified relationships';
  });
  const params = new URLSearchParams(window.location.search);
  const requested = params.get('artist');
  setFocus(byId.has(requested) ? requested : 'trey-anastasio');
  // Shareable paths: /connections/?from=primus&to=phish
  const sharedFrom = params.get('from'), sharedTo = params.get('to');
  const shared = byId.has(sharedFrom) && byId.has(sharedTo);
  fromInput.value = shared ? sharedFrom : 'gov-t-mule';
  toInput.value = shared ? sharedTo : 'grateful-dead';
  showPath();
  if (shared) get('cx-path-panel').scrollIntoView({block:'start'});
  if (requested && !shared) get('cx-focus-panel').scrollIntoView({block:'start'});
})();

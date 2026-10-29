/* Optional enhancement; the underlying dossier directory is HTML and works without JS. */
document.addEventListener('DOMContentLoaded', () => {
  const search = document.getElementById('da-query');
  const filter = document.getElementById('da-filter');
  const tiles = Array.from(document.querySelectorAll('.da-tile[data-search]'));
  const count = document.getElementById('da-match-count');
  if (!search || !filter || !count) return;
  function update() {
    const q = search.value.toLocaleLowerCase().trim();
    const f = filter.value;
    let shown = 0;
    for (const tile of tiles) {
      const visible = (!q || tile.dataset.search.includes(q)) && (f === 'all' || tile.dataset.kind === f);
      tile.hidden = !visible;
      if (visible) shown++;
    }
    count.textContent = `${shown} research dossiers shown`;
  }
  search.addEventListener('input', update);
  filter.addEventListener('change', update);
  update();
});

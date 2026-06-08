// Global search across all index entries
(async () => {
  const q = document.getElementById('q'); if (!q) return;
  let idx = null;
  let listEl = null;
  function ensurePanel(){
    if (listEl) return listEl;
    listEl = document.createElement('div');
    listEl.id = 'sresults';
    Object.assign(listEl.style, {
      position:'absolute', background:'#fff', border:'1px solid #e5e2d8',
      borderRadius:'4px', boxShadow:'0 6px 16px rgba(0,0,0,0.08)',
      maxHeight:'360px', overflowY:'auto', minWidth:'320px', zIndex:50,
      padding:'4px 0', fontSize:'13px'
    });
    document.body.appendChild(listEl);
    return listEl;
  }
  async function loadIdx(){
    if (idx) return idx;
    const base = q.closest('header').querySelector('.brand').getAttribute('href');
    const url = base.replace(/index\.html$/, '') + 'data/search-index.json';
    const r = await fetch(url); idx = await r.json();
    return idx;
  }
  function position(){
    const r = q.getBoundingClientRect();
    listEl.style.left = (r.left + window.scrollX) + 'px';
    listEl.style.top  = (r.bottom + window.scrollY + 4) + 'px';
    listEl.style.minWidth = r.width + 'px';
  }
  q.addEventListener('input', async () => {
    const v = q.value.trim().toLowerCase();
    if (!v){ if (listEl) listEl.style.display='none'; return; }
    const data = await loadIdx();
    ensurePanel(); position(); listEl.style.display='block';
    const matches = data.filter(d => d.n.toLowerCase().includes(v)).slice(0, 30);
    if (!matches.length){ listEl.innerHTML = '<div style="padding:10px 14px;color:#888">无匹配</div>'; return; }
    const base = q.closest('header').querySelector('.brand').getAttribute('href').replace(/index\.html$/, '');
    listEl.innerHTML = matches.map(m => {
      const cls = ({people:'person',concepts:'concept',entities:'entity'})[m.k] || '';
      const kindLabel = ({people:'人',concepts:'概念',entities:'实体',meetings:'纪要'})[m.k] || m.k;
      return `<a href="${base}${m.k}/${m.s}.html" style="display:flex;align-items:center;gap:8px;padding:6px 12px;color:#1a1a1a;text-decoration:none;border-bottom:1px solid #f0ebe0">
        <span style="font-size:10px;background:#f0ebe0;color:#5c4a2a;padding:1px 6px;border-radius:2px">${kindLabel}</span>
        <span>${m.n}</span></a>`;
    }).join('');
  });
  q.addEventListener('blur', () => setTimeout(()=>{ if(listEl) listEl.style.display='none'; }, 200));
  q.addEventListener('focus', () => { if (q.value.trim() && listEl) listEl.style.display='block'; });
  window.addEventListener('scroll', () => { if (listEl && listEl.style.display==='block') position(); });
  window.addEventListener('resize', () => { if (listEl && listEl.style.display==='block') position(); });
})();

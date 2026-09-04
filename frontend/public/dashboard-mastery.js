(() => {
  const API = '/api/dashboard';
  let latest = null;

  async function load() {
    try {
      const response = await fetch(API, { headers: { 'Content-Type': 'application/json' } });
      if (!response.ok) return;
      latest = await response.json();
      render();
    } catch (_) {}
  }

  function render() {
    if (!latest?.adaptive?.mastery_by_domain) return;
    const rows = latest.adaptive.mastery_by_domain;
    document.querySelectorAll('.mastery').forEach(card => {
      if (card.querySelector('.mastery-detail')) return;
      const name = card.querySelector('b')?.textContent?.replace(/^[^A-Za-z]+/, '').trim();
      const row = rows.find(x => x.domain === name);
      if (!row) return;
      const detail = document.createElement('div');
      detail.className = 'mastery-detail';
      detail.innerHTML = `<span><b>${row.attempts}/50</b> questions</span><span><b>${row.concepts_covered}/6</b> concepts</span><span><b>${row.accuracy}%</b> accuracy</span>`;
      card.appendChild(detail);
    });
  }

  const style = document.createElement('style');
  style.textContent = '.mastery-detail{display:flex;gap:14px;flex-wrap:wrap;margin-top:7px;font-size:.82rem;opacity:.8}.mastery-detail span{white-space:nowrap}.mastery-detail b{opacity:1}';
  document.head.appendChild(style);

  new MutationObserver(render).observe(document.body, { childList: true, subtree: true });
  setInterval(load, 3000);
  load();
})();

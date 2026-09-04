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

  function esc(value) {
    return String(value ?? '').replace(/[&<>\"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[ch]));
  }

  function render() {
    const rows = latest?.adaptive?.mastery_by_domain;
    if (!rows?.length) return;

    document.querySelectorAll('.mastery').forEach(card => {
      const name = card.querySelector('b')?.textContent?.replace(/^[^A-Za-z]+/, '').trim();
      const row = rows.find(x => x.domain === name);
      if (!row) return;

      let detail = card.querySelector('.mastery-detail');
      if (!detail) {
        detail = document.createElement('div');
        detail.className = 'mastery-detail';
        card.appendChild(detail);
      }
      detail.innerHTML = `<span><b>${row.attempts}</b> questions</span><span><b>${row.accuracy}%</b> accuracy</span><span><b>${row.concepts_covered}/${row.concepts_total}</b> concepts covered</span>`;

      let coverage = card.querySelector('.concept-coverage');
      if (!coverage) {
        coverage = document.createElement('div');
        coverage.className = 'concept-coverage';
        card.appendChild(coverage);
      }

      const concepts = row.concept_coverage || [];
      coverage.innerHTML = `<div class="concept-title">Concept Coverage</div><div class="concept-grid">${concepts.map(c => `<span class="concept ${c.covered ? 'covered' : 'uncovered'}"><span>${c.covered ? '✓' : '○'}</span>${esc(c.name)}</span>`).join('')}</div>`;
    });
  }

  const style = document.createElement('style');
  style.textContent = `
    .mastery-detail{display:flex;gap:14px;flex-wrap:wrap;margin-top:7px;font-size:.82rem;opacity:.8}
    .mastery-detail span{white-space:nowrap}
    .mastery-detail b{opacity:1}
    .concept-coverage{margin-top:12px;padding-top:10px;border-top:1px solid rgba(127,127,127,.18)}
    .concept-title{font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;opacity:.72}
    .concept-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:6px 14px}
    .concept{font-size:.82rem;line-height:1.35;display:flex;gap:7px;align-items:flex-start}
    .concept span{width:16px;flex:0 0 16px;font-weight:700}
    .concept.covered span{opacity:1}
    .concept.uncovered{opacity:.48}
  `;
  document.head.appendChild(style);

  new MutationObserver(render).observe(document.body, { childList: true, subtree: true });
  setInterval(load, 3000);
  load();
})();

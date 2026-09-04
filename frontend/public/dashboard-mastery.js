(() => {
  const DASH_API = '/api/dashboard';
  const STUDY_API = '/api/study-plan';
  let dashboardData = null;
  let studyData = null;
  let dashboardBusy = false;
  let studyBusy = false;

  async function loadDashboard() {
    if (dashboardBusy) return;
    dashboardBusy = true;
    try {
      const response = await fetch(DASH_API, { cache: 'no-store' });
      if (response.ok) {
        dashboardData = await response.json();
        renderDashboard();
      }
    } catch (_) {} finally { dashboardBusy = false; }
  }

  async function loadStudy() {
    if (studyBusy) return;
    studyBusy = true;
    try {
      const response = await fetch(STUDY_API, { cache: 'no-store' });
      if (response.ok) {
        studyData = await response.json();
        renderStudy();
      }
    } catch (_) {} finally { studyBusy = false; }
  }

  function esc(value) {
    return String(value ?? '').replace(/[&<>\"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[ch]));
  }

  function renderDashboard() {
    if (!dashboardData?.adaptive?.mastery_by_domain) return;
    const loading = [...document.querySelectorAll('.loading')].find(x => /Loading dashboard/i.test(x.textContent || ''));
    if (!loading) return;
    const s = dashboardData.stats || {};
    loading.className = 'dashboard-fallback';
    loading.innerHTML = `
      <div class="section"><h2>Historical Progress</h2></div>
      <div class="grid2">
        <div class="stat"><div>Questions Completed</div><strong>${esc(s.attempted ?? 0)}</strong></div>
        <div class="stat"><div>Lifetime Accuracy</div><strong>${esc(s.accuracy ?? 0)}%</strong></div>
      </div>
      <div class="section"><h2>What To Study Next</h2></div>
      <p>Use your mastery areas below to focus your next study session.</p>
      <div class="section"><h2>Mastery by Domain</h2></div>
      ${dashboardData.adaptive.mastery_by_domain.map(renderCard).join('')}
    `;
  }

  function renderCard(row) {
    const icons = {New:'⚪',Learning:'🟡',Weak:'🔴',Mastered:'🟢'};
    const concepts = row.concept_coverage || [];
    return `<div class="mastery">
      <b>${icons[row.status] || '⚪'} ${esc(row.domain)}</b><span>${esc(row.status)}</span>
      <div class="mastery-detail"><span><b>${esc(row.attempts)}</b> questions</span><span><b>${esc(row.accuracy)}%</b> accuracy</span><span><b>${esc(row.concepts_covered)}/${esc(row.concepts_total)}</b> concepts covered</span></div>
      <div class="concept-coverage"><div class="concept-title">Concept Coverage</div><div class="concept-grid">${concepts.map(c => `<span class="concept ${c.covered ? 'covered' : 'uncovered'}"><span>${c.covered ? '✓' : '○'}</span>${esc(c.name)}</span>`).join('')}</div></div>
    </div>`;
  }

  function renderStudy() {
    if (!studyData?.goal || !studyData?.plan) return;
    const loading = [...document.querySelectorAll('.loading')].find(x => /Loading study plan/i.test(x.textContent || ''));
    if (!loading) return;
    const g = studyData.goal;
    const p = studyData.plan;
    loading.className = 'study-fallback';
    loading.innerHTML = `
      <div class="section"><h2>Current Study Plan</h2></div>
      <div class="info">📅 Exam target: <b>${esc(g.target_date)}</b> · <b>${esc(g.part)}</b> · <b>${esc(g.daily_minutes)} minutes/day</b></div>
      <div class="card"><b>Study goal loaded.</b><br/><span>${esc(p.message || 'Your study plan is ready.')}</span></div>
      ${p.days_remaining != null ? `<div class="grid2"><div class="stat"><div>Days Remaining</div><strong>${esc(p.days_remaining)}</strong></div><div class="stat"><div>Daily Target</div><strong>${esc(p.daily_minutes)} min</strong></div></div>` : ''}
      ${p.focus_topics?.length ? `<div class="section"><h2>Focus Areas</h2></div>${p.focus_topics.map(x => `<div class="card">🎯 <b>${esc(x)}</b></div>`).join('')}` : ''}
      ${p.session?.length ? `<div class="section"><h2>Suggested Session</h2></div>${p.session.map(x => `<p>• ${esc(x)}</p>`).join('')}` : ''}
    `;
  }

  const style = document.createElement('style');
  style.textContent = `
    .mastery-detail{display:flex;gap:14px;flex-wrap:wrap;margin-top:7px;font-size:.82rem;opacity:.8}
    .mastery-detail span{white-space:nowrap}
    .concept-coverage{margin-top:12px;padding-top:10px;border-top:1px solid rgba(127,127,127,.18)}
    .concept-title{font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;opacity:.72}
    .concept-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:6px 14px}
    .concept{font-size:.82rem;line-height:1.35;display:flex;gap:7px;align-items:flex-start}
    .concept span{width:16px;flex:0 0 16px;font-weight:700}
    .concept.uncovered{opacity:.48}
    .dashboard-fallback,.study-fallback{display:block}
    .dashboard-fallback .mastery{margin-top:12px}
  `;
  document.head.appendChild(style);

  function renderAll() { renderDashboard(); renderStudy(); }
  new MutationObserver(renderAll).observe(document.body, { childList: true, subtree: true });
  setInterval(() => { loadDashboard(); loadStudy(); }, 2000);
  loadDashboard();
  loadStudy();
})();
// ── Vacantes Grid & Filtering ────────────────────────────────────────────────
async function loadVacantes() {
  try {
    const res = await fetch(`${API_BASE}/vacantes`);
    const data = await res.json();
    allVacantes = data.vacantes || [];
    const statEl = document.getElementById('stat-vacantes');
    if (statEl) statEl.textContent = allVacantes.length;
    renderVacantes();
    populateRecruiterVacantesSelect();
  } catch {
    if (vacantesGrid) {
      vacantesGrid.innerHTML = `<div class="loading-state" style="color:var(--rose)">
        <span>⚠ No se pudo conectar con la API en localhost:8000</span></div>`;
    }
  }
}

function renderVacantes() {
  if (!vacantesGrid) return;
  const filtered = currentFilter === 'all'
    ? allVacantes
    : allVacantes.filter(v => v.tipo === currentFilter);

  if (!filtered.length) {
    vacantesGrid.innerHTML = '<div class="loading-state"><span>No hay vacantes en esta categoría</span></div>';
    return;
  }

  vacantesGrid.innerHTML = filtered.map(v => `
    <div class="vacante-card">
      <div class="vacante-area-tag">${escHtml(v.area)}</div>
      <div class="vacante-title">${escHtml(v.titulo)}</div>
      <div class="vacante-company">${escHtml(v.empresa)} · ${escHtml(v.tipo_empresa)}</div>
      <div class="vacante-meta">
        <span class="badge badge-tipo">${escHtml(v.tipo)}</span>
        <span class="badge badge-nivel">${escHtml(v.nivel)}</span>
        <span class="badge badge-salary">💰 ${escHtml(v.salario_rango || 'Transparente')}</span>
        ${v.remoto ? '<span class="badge badge-remoto">🌐 Remoto</span>' : ''}
      </div>
      <div class="vacante-skills">
        ${(v.requisitos || []).slice(0, 6).map(r => `<span class="vacante-skill">${escHtml(r)}</span>`).join('')}
        ${v.requisitos.length > 6 ? `<span class="vacante-skill">+${v.requisitos.length - 6}</span>` : ''}
      </div>
    </div>
  `).join('');
}

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderVacantes();
  });
});

// ── Modo Recruiter Logic ──────────────────────────────────────────────────────
function renderRecruiterCandidates() {
  if (!recruiterCandList) return;
  recruiterCandList.innerHTML = sampleCandidates.map(c => `
    <div class="recruiter-cand-item">
      <div>
        <strong style="color:var(--violet-light);">${escHtml(c.nombre_anonimizado)}</strong>
        <p style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px;">${escHtml(c.cv_text.slice(0, 120))}...</p>
      </div>
      <span class="badge badge-nivel">Anonimizado</span>
    </div>
  `).join('');
}

function populateRecruiterVacantesSelect() {
  if (!recruiterVacanteSelect) return;
  recruiterVacanteSelect.innerHTML = '<option value="">-- Cargar desde BD de vacantes curadas --</option>';
  allVacantes.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.id;
    opt.textContent = `${v.titulo} (${v.empresa}) — ${v.salario_rango || 'Transparente'}`;
    recruiterVacanteSelect.appendChild(opt);
  });
}

if (recruiterVacanteSelect) {
  recruiterVacanteSelect.addEventListener('change', () => {
    const vId = recruiterVacanteSelect.value;
    const vacante = allVacantes.find(v => v.id === vId);
    if (vacante && recruiterVacanteText) {
      recruiterVacanteText.value = `${vacante.titulo} en ${vacante.empresa} (${vacante.nivel}). Requisitos: ${vacante.requisitos.join(', ')}. ${vacante.descripcion}`;
    }
  });
}

if (recruiterLoadSampleBtn) {
  recruiterLoadSampleBtn.addEventListener('click', () => {
    renderRecruiterCandidates();
    showToast('3 perfiles anonimizados listos en el pool', 'info');
  });
}

if (recruiterRunBtn) {
  recruiterRunBtn.addEventListener('click', handleRunRecruiter);
}

async function handleRunRecruiter() {
  const vacanteText = recruiterVacanteText.value.trim();
  if (!vacanteText) {
    showToast('Por favor selecciona o escribe la descripción de la vacante', 'error');
    return;
  }

  recruiterRunBtn.disabled = true;
  recruiterRunBtn.innerHTML = '<span class="spinner"></span> Evaluando candidatos con evidencia...';

  try {
    const res = await fetch(`${API_BASE}/recruiter/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        descripcion_vacante: vacanteText,
        candidatos: sampleCandidates
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error en evaluación de recruiter');

    renderRecruiterResults(data.ranking);
    showToast('Ranking objetivo generado con éxito', 'success');
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    recruiterRunBtn.disabled = false;
    recruiterRunBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Evaluar &amp; Rankear con Evidencia';
  }
}

function renderRecruiterResults(ranking) {
  if (!recruiterResultsCards) return;
  recruiterResultsCards.innerHTML = ranking.map((c, i) => {
    const scoreNum = parseInt(c.match_score) || 0;
    const ringColor = scoreNum >= 70 ? 'var(--emerald)' : scoreNum >= 40 ? 'var(--amber)' : 'var(--rose)';
    return `
      <article class="match-card">
        <div class="card-header">
          <div>
            <div class="card-title">#${i + 1} ${escHtml(c.nombre_anonimizado)}</div>
            <div class="card-company">Evaluado objetivamente sin sesgo de identidad</div>
          </div>
          <div style="font-size:1.4rem;font-weight:700;color:${ringColor}">${c.match_score}</div>
        </div>
        <div class="card-section-label">Evidencia Comprobada en CV</div>
        <p class="card-reason">${escHtml(c.razon_del_match)}</p>
        <div class="card-section-label">Brechas Detectadas</div>
        <p style="font-size:0.85rem;color:var(--text-secondary);">${escHtml(c.brechas_detectadas || 'Ninguna crítica')}</p>
        <div style="margin-top:12px;font-size:0.78rem;color:var(--emerald-light);">
          ✓ Recomendación auditable con evidencia
        </div>
      </article>
    `;
  }).join('');
  recruiterResultsBox.hidden = false;
  recruiterResultsBox.scrollIntoView({ behavior: 'smooth' });
}

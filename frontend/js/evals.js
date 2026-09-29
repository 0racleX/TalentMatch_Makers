// ── Evals Suite UI ────────────────────────────────────────────────────────────
if (runEvalsBtn) {
  runEvalsBtn.addEventListener('click', handleRunEvals);
}

async function handleRunEvals() {
  runEvalsBtn.disabled = true;
  runEvalsBtn.innerHTML = `<span class="spinner"></span> Corriendo suite de evals...`;

  evalsTbody.innerHTML = Array.from({length: 12}, (_, i) => `
    <tr>
      <td><span class="eval-id">cargando...</span></td>
      <td>—</td>
      <td><span class="badge-running">Corriendo</span></td>
      <td>—</td><td>—</td><td>—</td>
    </tr>
  `).join('');

  try {
    const res = await fetch(`${API_BASE}/evals/run?use_cache=true`, { method: 'POST' });
    const jsonRes = await res.json();
    evalsData = jsonRes.data || jsonRes;
    renderEvals(evalsData);
  } catch (err) {
    showToast('Error corriendo evals. ¿Está la API corriendo?', 'error');
    evalsTbody.innerHTML = `<tr><td colspan="6" style="padding:40px;text-align:center;color:var(--rose)">Error: ${escHtml(err.message)}</td></tr>`;
  } finally {
    runEvalsBtn.disabled = false;
    runEvalsBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Correr Evals (Cache Inteligente)`;
  }
}

function renderEvals(data) {
  const { total, passed, failed, score_pct, casos } = data;

  if (evalsTotal) evalsTotal.textContent = total;
  if (evalsPassed) evalsPassed.textContent = passed;
  if (evalsFailed) evalsFailed.textContent = failed;
  if (evalsScorePct) evalsScorePct.textContent = `${score_pct}%`;

  const circumference = 251.2;
  const offset = circumference - (score_pct / 100) * circumference;
  if (evalsRingFill) evalsRingFill.style.strokeDashoffset = offset;

  lastEvalDetails = {};
  if (!evalsTbody) return;
  evalsTbody.innerHTML = (casos || []).map(caso => {
    lastEvalDetails[caso.id] = caso;
    return `
      <tr>
        <td><span class="eval-id">${escHtml(caso.id)}</span></td>
        <td><span class="eval-type">${escHtml(caso.tipo)}</span></td>
        <td>${caso.passed ? '<span class="badge-pass">✓ Pass</span>' : '<span class="badge-fail">✗ Fail</span>'}</td>
        <td><span class="eval-output">${escHtml(caso.output_resumen)}</span></td>
        <td><span class="eval-why">${escHtml(caso.why_it_matters)}</span></td>
        <td><button class="eval-detail-btn" onclick="openModal('${escHtml(caso.id)}')">Ver criterios</button></td>
      </tr>
    `;
  }).join('');
}

// ── Modal de Criterios ────────────────────────────────────────────────────────
function openModal(casoId) {
  const caso = lastEvalDetails[casoId];
  if (!caso) return;
  modalTitle.textContent = `Criterios: ${casoId}`;
  modalBody.innerHTML = (caso.criterios || []).map(c => `
    <div class="criterio-row">
      <span class="criterio-icon">${c.resultado ? '✅' : '❌'}</span>
      <div>
        <div class="criterio-name">${escHtml(c.criterio)}</div>
        <div class="criterio-detail">${escHtml(c.detalle)}</div>
      </div>
    </div>
  `).join('') || '<p style="color:var(--text-muted)">Sin criterios registrados</p>';
  modalOverlay.hidden = false;
}

if (modalClose) {
  modalClose.addEventListener('click', () => { modalOverlay.hidden = true; });
}
if (modalOverlay) {
  modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) modalOverlay.hidden = true; });
}
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') modalOverlay.hidden = true; });

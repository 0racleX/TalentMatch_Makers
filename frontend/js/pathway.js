// ── Simulador Interactivo 'Camino a la Vacante' ────────────────────────────────
async function triggerSimulation(rec, skill, card, index) {
  const currentCv = currentTab === 'text' ? cvTextarea.value.trim() : "Candidato con perfil tech analizado.";
  showToast(`Simulando adquisición de '${skill}'...`, 'info');

  try {
    const vacanteObj = allVacantes.find(v => v.titulo === rec.titulo_oportunidad) || { id: "v001" };
    const res = await fetch(`${API_BASE}/simular-brechas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cv_text: currentCv.length > 20 ? currentCv : "Desarrollador con experiencia técnica y proyectos reales.",
        vacante_id: vacanteObj.id,
        habilidades_aprendidas: [skill]
      })
    });
    const simResponse = await res.json();
    const simData = simResponse.simulacion || simResponse;

    const projectedScore = parseInt(simData.score_proyectado) || 85;
    const circumference = 163.36;
    const newOffset = circumference - (projectedScore / 100) * circumference;

    const ring = card.querySelector('.ring-fill-card');
    const label = card.querySelector(`#score-label-${index}`);
    if (ring && label) {
      ring.style.stroke = '#10b981';
      ring.style.strokeDashoffset = newOffset;
      label.style.color = '#10b981';
      label.textContent = `${projectedScore}%`;
    }

    modalTitle.textContent = `🎯 Proyección de Carrera: ${rec.titulo_oportunidad}`;
    modalBody.innerHTML = `
      <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:0.9rem;color:var(--text-secondary)">Score Original: <strong>${simData.score_original}</strong></span>
        <span style="margin:0 12px;color:var(--emerald-light);font-size:1.2rem">➔</span>
        <span style="font-size:1.1rem;font-weight:700;color:var(--emerald-light)">Score Proyectado: ${simData.score_proyectado} (${simData.incremento_estimado})</span>
      </div>
      <div class="card-pathway-box" style="margin-bottom:16px;">
        <strong>Habilidad Simulada:</strong> <span class="badge badge-salary">${escHtml(skill)}</span>
      </div>
      <p style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6;margin-bottom:16px;">
        ${escHtml(simData.analisis_proyeccion)}
      </p>
      ${simData.brechas_restantes && simData.brechas_restantes.length ? `
        <div class="card-section-label">Brechas restantes tras este curso:</div>
        <div class="card-gaps-list">${simData.brechas_restantes.map(b => `<span class="gap-tag">${escHtml(b)}</span>`).join('')}</div>
      ` : '<div style="color:var(--emerald-light);font-size:0.85rem">¡Cubre el 100% de los requisitos técnicos clave!</div>'}
    `;
    modalOverlay.hidden = false;

  } catch (err) {
    showToast(`Error en la simulación: ${err.message}`, 'error');
  }
}

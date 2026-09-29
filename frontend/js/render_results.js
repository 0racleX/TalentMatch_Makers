// ── Render Results con Camino a la Vacante ────────────────────────────────────
function renderResults(output) {
  cardsGrid.innerHTML = '';
  profilingCard.innerHTML = '';
  profilingCard.hidden = true;

  const mode = output.modo;
  const recs = output.recomendaciones || [];
  const perfil = output.perfil_candidato;
  const total = output.total_vacantes_evaluadas;

  // Validación de Documento: Si no es un CV legítimo
  if (mode === 'documento_invalido') {
    resultsSubtitle.textContent = 'Documento no reconocido como Curriculum Vitae / Hoja de Vida.';
    resultsMeta.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      Modo: <strong style="color:#f87171">Documento No Válido</strong> · Tipo: <strong>${escHtml(output.tipo_documento || 'No CV')}</strong>
      ${output.inyeccion_detectada ? '· <span style="color:var(--amber)">🛡️ Inyección neutralizada</span>' : ''}
    `;
    cardsGrid.innerHTML = buildInvalidDocumentHTML(output);
    const retryBtn = document.getElementById('btn-invalid-doc-retry');
    if (retryBtn) retryBtn.addEventListener('click', resetToUpload);
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }

  resultsMeta.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    Evaluadas ${total} vacantes verificadas · Modo: <strong>${mode === 'match' ? 'Match Directo Anclado en Evidencia' : 'Ruta de Formación y Perfilamiento'}</strong>
    ${output.inyeccion_detectada ? '· <span style="color:var(--amber)">🛡️ Inyección neutralizada por seguridad</span>' : ''}
  `;

  if (mode === 'match' && recs.length > 0) {
    resultsSubtitle.textContent = `Encontramos ${recs.length} vacante${recs.length !== 1 ? 's' : ''} con evidencia clara. Si tienes brechas, usa el simulador para proyectar tu crecimiento.`;
    recs.forEach((rec, i) => {
      const card = buildMatchCard(rec, i);
      cardsGrid.appendChild(card);
    });
  } else if (mode === 'profiling' && perfil) {
    resultsSubtitle.textContent = 'No forzamos matches falsos. Aquí está tu plan de carrera y los recursos concretos para cerrar la brecha.';
    if (recs.length > 0) {
      recs.forEach((rec, i) => cardsGrid.appendChild(buildMatchCard(rec, i)));
    }
    profilingCard.innerHTML = buildProfilingHTML(perfil);
    profilingCard.hidden = false;
  } else {
    resultsSubtitle.textContent = 'No se encontraron resultados. Intenta con una descripción más detallada.';
  }

  resultsSection.hidden = false;
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buildMatchCard(rec, index) {
  const score = parseInt(rec.match_score) || 0;
  const circumference = 163.36;
  const offset = circumference - (score / 100) * circumference;
  const ringColor = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';

  const gaps = rec.brechas_identificadas
    ? rec.brechas_identificadas.split(',').map(g => g.trim()).filter(Boolean)
    : [];

  const card = document.createElement('article');
  card.className = 'match-card';
  card.id = `match-card-${index}`;
  card.style.animationDelay = `${index * 0.12}s`;

  const recursos = rec.recursos_recomendados || [];
  let pathwayHTML = '';
  if (recursos.length > 0) {
    pathwayHTML = `
      <div class="card-pathway-box">
        <div class="pathway-title">
          <span>🛣️ Camino a la Vacante (Acelera tu Match)</span>
        </div>
        ${recursos.map(r => `
          <div class="pathway-resource-item">
            <div>
              <strong>${escHtml(r.titulo)}</strong>
              <div style="font-size:0.75rem;color:var(--text-muted);">
                ${escHtml(r.proveedor)} · <span style="color:var(--emerald-light)">${escHtml(r.costo)}</span>
              </div>
            </div>
            <div style="display:flex;gap:6px;align-items:center;">
              <a href="${escHtml(r.url)}" target="_blank" rel="noopener" style="font-size:0.75rem;color:var(--violet-light);">Ver ↗</a>
              <button class="btn-simulate" data-skill="${escHtml(r.habilidad)}" data-vacante="${escHtml(rec.titulo_oportunidad)}" data-score="${score}">
                Simular +${r.impacto_match_estimado}%
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  card.innerHTML = `
    <div class="card-header">
      <div>
        <div class="card-title">${escHtml(rec.titulo_oportunidad)}</div>
        <div class="card-company">${escHtml(rec.empresa)} · ${escHtml(rec.tipo_empresa)}</div>
      </div>
      <div class="card-score-ring">
        <svg viewBox="0 0 52 52">
          <circle cx="26" cy="26" r="26" class="ring-bg-card"/>
          <circle cx="26" cy="26" r="26" class="ring-fill-card"
            style="stroke:${ringColor}; stroke-dashoffset:${circumference};"
            data-offset="${offset}"/>
        </svg>
        <div class="card-score-label" id="score-label-${index}" style="color:${ringColor}">${score}%</div>
      </div>
    </div>
    <div class="card-badges">
      <span class="badge badge-tipo">${escHtml(rec.tipo)}</span>
      <span class="badge badge-nivel">${escHtml(rec.nivel)}</span>
      ${rec.salario_rango ? `<span class="badge badge-salary">💰 ${escHtml(rec.salario_rango)}</span>` : ''}
      ${rec.remoto !== undefined ? `<span class="badge badge-remoto">${rec.remoto ? '🌐 Remoto' : '📍 Presencial'}</span>` : ''}
    </div>
    <div class="card-section-label">Evidencia de por qué encajas</div>
    <p class="card-reason">${escHtml(rec.razon_del_match)}</p>
    ${gaps.length ? `
      <div class="card-section-label">Brechas específicas a cerrar</div>
      <div class="card-gaps-list">${gaps.map(g => `<span class="gap-tag">${escHtml(g)}</span>`).join('')}</div>
    ` : ''}
    ${pathwayHTML}
    <div class="card-footer">
      <span class="card-empresa-tag">${escHtml(rec.tipo_empresa)}</span>
      ${rec.link
        ? `<a href="${escHtml(rec.link)}" target="_blank" rel="noopener" class="card-link">Postular directo ↗</a>`
        : `<span class="card-no-link">Link no publicado en BD</span>`}
    </div>
  `;

  requestAnimationFrame(() => {
    setTimeout(() => {
      const ring = card.querySelector('.ring-fill-card');
      if (ring) ring.style.strokeDashoffset = offset;
    }, 100 + index * 120);
  });

  card.querySelectorAll('.btn-simulate').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const skill = btn.dataset.skill;
      triggerSimulation(rec, skill, card, index);
    });
  });

  return card;
}

function buildProfilingHTML(p) {
  const skillsHas = (p.habilidades_detectadas || []).map(s => `<span class="skill-tag has">${escHtml(s)}</span>`).join('');
  const skillsRec = (p.habilidades_recomendadas || []).map(s => `<span class="skill-tag rec">${escHtml(s)}</span>`).join('');
  const recursos = (p.recursos_recomendados || []).map(r => `
    <div class="pathway-resource-item">
      <div>
        <strong>${escHtml(r.titulo)}</strong>
        <div style="font-size:0.75rem;color:var(--text-muted);">${escHtml(r.proveedor)} · <span style="color:var(--emerald-light)">${escHtml(r.costo)}</span></div>
      </div>
      <a href="${escHtml(r.url)}" target="_blank" rel="noopener" class="btn btn-ghost btn-sm">Iniciar Curso ↗</a>
    </div>
  `).join('');

  return `
    <div class="profiling-header">
      <div class="profiling-icon">🧭</div>
      <div>
        <div class="profiling-title">Perfilamiento Profesional &amp; Camino a la Vacante</div>
        <div class="profiling-subtitle">No te dejamos en silencio: aquí está tu diagnóstico objetivo y cómo acelerar</div>
      </div>
    </div>
    <div style="margin-bottom:20px">
      <div class="card-section-label">Diagnóstico de tu perfil</div>
      <p style="color:var(--text-secondary);font-size:0.9rem;line-height:1.65">${escHtml(p.resumen_perfil)}</p>
    </div>
    <div class="profiling-grid">
      <div class="profiling-section">
        <h4>Rol sugerido en el mercado</h4>
        <p style="font-size:0.88rem;color:var(--text-secondary)">${escHtml(p.rol_sugerido)}</p>
      </div>
      <div class="profiling-section">
        <h4>Tipo de empresa ideal</h4>
        <p style="font-size:0.88rem;color:var(--text-secondary)">${escHtml(p.tipo_empresa_ideal)}</p>
      </div>
      <div class="profiling-section">
        <h4>Habilidades que ya tienes</h4>
        <div class="skill-tags">${skillsHas || '<span style="color:var(--text-muted);font-size:0.82rem">No detectadas</span>'}</div>
      </div>
      <div class="profiling-section">
        <h4>Ruta recomendada para aprender</h4>
        <div class="skill-tags">${skillsRec}</div>
      </div>
    </div>
    ${recursos ? `
      <div style="margin-top:20px;">
        <div class="card-section-label">Recursos de Formación Curados para tu Perfil</div>
        <div class="card-pathway-box">${recursos}</div>
      </div>
    ` : ''}
    <div class="profiling-message" style="margin-top:16px;">${escHtml(p.mensaje)}</div>
  `;
}

function buildInvalidDocumentHTML(output) {
  const tipoDoc = output.tipo_documento || 'documento_no_cv';
  const motivosMap = {
    guia_laboratorio: {
      titulo: "Práctica de Laboratorio / Guía Experimental Detectada",
      icono: "🔬",
      badge: "Guía de Laboratorio Académica"
    },
    tarea_academica: {
      titulo: "Tarea o Taller Académico Detectado",
      icono: "📝",
      badge: "Asignación / Taller de Clase"
    },
    manual_tecnico: {
      titulo: "Manual Técnico o Guía de Software Detectado",
      icono: "📖",
      badge: "Documentación Técnica"
    },
    factura_comercial: {
      titulo: "Documento Contable / Factura Detectada",
      icono: "🧾",
      badge: "Factura Comercial"
    },
    folleto_publicitario: {
      titulo: "Folleto Publicitario / Catálogo Turístico Detectado",
      icono: "🏖️",
      badge: "Brochure Comercial / Publicidad"
    },
    pdf_sin_texto: {
      titulo: "Archivo Gráfico sin Capa de Texto Digital",
      icono: "🖼️",
      badge: "Documento Gráfico No Seleccionable"
    }
  };

  const meta = motivosMap[tipoDoc] || {
    titulo: "Documento no reconocido como Hoja de Vida",
    icono: "📄⚠️",
    badge: "Archivo no compatible"
  };

  const mensaje = output.mensaje_validacion ||
    "El documento proporcionado no presenta el formato ni contenido de una hoja de vida o perfil profesional de un candidato.";

  return `
    <div class="invalid-doc-card">
      <div class="invalid-doc-icon">${meta.icono}</div>
      <div class="invalid-doc-badge">${meta.badge}</div>
      <h3 class="invalid-doc-title">${meta.titulo}</h3>
      <p class="invalid-doc-desc">
        ${escHtml(mensaje)}
      </p>
      <div class="invalid-doc-notice">
        <strong>🛡️ Principio de Integridad de TalentMatch AI:</strong>
        A diferencia de plataformas tradicionales que asignarían puntajes arbitrarios a guías de laboratorio o tareas escolares, nuestro motor multiagente protege la veracidad del matching y rechaza documentos que no correspondan a una trayectoria profesional legítima.
      </div>
      <div style="margin-top: 24px;">
        <button class="btn btn-primary" id="btn-invalid-doc-retry">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Subir un Curriculum Vitae Real
        </button>
      </div>
    </div>
  `;
}

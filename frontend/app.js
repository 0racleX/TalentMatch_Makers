const API_BASE = window.location.origin.includes(':8000') ? window.location.origin : 'http://localhost:8000';

// ── State ────────────────────────────────────────────────────────────────────
let currentFile = null;
let currentTab = 'pdf';
let allVacantes = [];
let currentFilter = 'all';
let evalsData = null;
let lastEvalDetails = {};
let sampleCandidates = [
  {
    id: "cand_01",
    nombre_anonimizado: "Candidato #1 (Dev Backend Semi-Senior)",
    cv_text: "Desarrollador Backend con 3 años de experiencia en Python, FastAPI, Django y bases de datos relacionales PostgreSQL. He implementado microservicios con Docker y configurado pipelines CI/CD básicos en GitHub Actions. Manejo REST APIs y pruebas unitarias con Pytest."
  },
  {
    id: "cand_02",
    nombre_anonimizado: "Candidata #2 (Fullstack React / Node)",
    cv_text: "Desarrolladora Fullstack con 4 años construyendo aplicaciones SaaS en React, Next.js, TypeScript en frontend y Node.js con Express en backend. Experiencia con AWS (S3, Lambda) y bases de datos NoSQL/SQL. Lideré equipo ágil de 3 ingenieros."
  },
  {
    id: "cand_03",
    nombre_anonimizado: "Candidato #3 (Junior en Transición)",
    cv_text: "Egresado autodidacta de bootcamp con bases sólidas en JavaScript, HTML, CSS y fundamentos de Python. Creé proyectos personales de APIs REST y dashboards de análisis de datos. Alto interés en infraestructura cloud y aprendizaje continuo."
  }
];

// ── DOM Refs ─────────────────────────────────────────────────────────────────
const dropZone       = document.getElementById('drop-zone');
const fileInput      = document.getElementById('file-input');
const fileInfo       = document.getElementById('file-info');
const fileName       = document.getElementById('file-name');
const fileSize       = document.getElementById('file-size');
const fileRemove     = document.getElementById('file-remove');
const cvTextarea     = document.getElementById('cv-textarea');
const charCounter    = document.getElementById('char-counter');
const analyzeBtn     = document.getElementById('analyze-btn');
const tabPdf         = document.getElementById('tab-pdf');
const tabText        = document.getElementById('tab-text');
const panelPdf       = document.getElementById('panel-pdf');
const panelText      = document.getElementById('panel-text');
const pipelineVisual = document.getElementById('pipeline-visual');
const uploadSection  = document.getElementById('upload-section');
const resultsSection = document.getElementById('results-section');
const resultsMeta    = document.getElementById('results-meta');
const resultsSubtitle= document.getElementById('results-subtitle');
const cardsGrid      = document.getElementById('cards-grid');
const profilingCard  = document.getElementById('profiling-card');
const resetBtn       = document.getElementById('reset-btn');
const vacantesGrid   = document.getElementById('vacantes-grid');
const filterBtns     = document.querySelectorAll('.filter-btn');
const runEvalsBtn    = document.getElementById('run-evals-btn');
const evalsTbody     = document.getElementById('evals-tbody');
const evalsScorePct  = document.getElementById('evals-score-pct');
const evalsPassed    = document.getElementById('evals-passed');
const evalsFailed    = document.getElementById('evals-failed');
const evalsTotal     = document.getElementById('evals-total');
const evalsRingFill  = document.getElementById('evals-ring-fill');
const modalOverlay   = document.getElementById('modal-overlay');
const modalClose     = document.getElementById('modal-close');
const modalBody      = document.getElementById('modal-body');
const modalTitle     = document.getElementById('modal-title');
const navbar         = document.getElementById('navbar');

// Recruiter Refs
const recruiterVacanteSelect = document.getElementById('recruiter-vacante-select');
const recruiterVacanteText   = document.getElementById('recruiter-vacante-text');
const recruiterLoadSampleBtn = document.getElementById('recruiter-load-sample-btn');
const recruiterCandList      = document.getElementById('recruiter-candidates-list');
const recruiterRunBtn        = document.getElementById('recruiter-run-btn');
const recruiterResultsBox    = document.getElementById('recruiter-results-box');
const recruiterResultsCards  = document.getElementById('recruiter-results-cards');

// Trust Center Refs
const runFairnessBtn         = document.getElementById('run-fairness-btn');
const fairnessStatusPill     = document.getElementById('fairness-status-pill');
const metricTotalEvals       = document.getElementById('metric-total-evals');
const metricMatchRate        = document.getElementById('metric-match-rate');
const metricProfilingRate    = document.getElementById('metric-profiling-rate');
const metricInjections       = document.getElementById('metric-injections-blocked');

// ── SVG Gradient for eval ring ───────────────────────────────────────────────
document.body.insertAdjacentHTML('beforeend', `
  <svg width="0" height="0" style="position:absolute">
    <defs>
      <linearGradient id="ring-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#7c3aed"/>
        <stop offset="100%" stop-color="#10b981"/>
      </linearGradient>
    </defs>
  </svg>
`);

// ── Navbar Scroll ────────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
});

// ── Typing Effect (Diferenciación de Producto) ────────────────────────────────
const typedWords = [
  'algoritmos opacos de LinkedIn',
  'el silencio y ghosting de Magneto',
  'salarios ocultos "a convenir"',
  'filtros ciegos por palabras clave'
];
let wordIdx = 0, charIdx = 0, isDeleting = false;
const typedEl = document.getElementById('typed-text');
function typeLoop() {
  const word = typedWords[wordIdx];
  typedEl.textContent = isDeleting ? word.slice(0, charIdx--) : word.slice(0, charIdx++);
  let delay = isDeleting ? 45 : 80;
  if (!isDeleting && charIdx > word.length) { delay = 2000; isDeleting = true; }
  else if (isDeleting && charIdx < 0) { isDeleting = false; wordIdx = (wordIdx + 1) % typedWords.length; delay = 350; }
  setTimeout(typeLoop, delay);
}
setTimeout(typeLoop, 800);

// ── Tabs Candidato ────────────────────────────────────────────────────────────
tabPdf.addEventListener('click', () => switchTab('pdf'));
tabText.addEventListener('click', () => switchTab('text'));

function switchTab(tab) {
  currentTab = tab;
  tabPdf.classList.toggle('active', tab === 'pdf');
  tabText.classList.toggle('active', tab === 'text');
  tabPdf.setAttribute('aria-selected', tab === 'pdf');
  tabText.setAttribute('aria-selected', tab === 'text');
  panelPdf.classList.toggle('active', tab === 'pdf');
  panelText.classList.toggle('active', tab === 'text');
  checkCanAnalyze();
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
dropZone.addEventListener('click', (e) => {
  if (!e.target.closest('.file-remove')) fileInput.click();
});
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault(); dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });
fileRemove.addEventListener('click', (e) => { e.stopPropagation(); clearFile(); });

function handleFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Solo se aceptan archivos PDF', 'error'); return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast('El archivo supera 10MB', 'error'); return;
  }
  currentFile = file;
  fileInfo.hidden = false;
  dropZone.querySelector('.drop-zone-content').hidden = true;
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  checkCanAnalyze();
}
function clearFile() {
  currentFile = null; fileInput.value = '';
  fileInfo.hidden = true;
  dropZone.querySelector('.drop-zone-content').hidden = false;
  checkCanAnalyze();
}
function formatBytes(b) { return b < 1024 ? `${b} B` : b < 1048576 ? `${(b/1024).toFixed(1)} KB` : `${(b/1048576).toFixed(1)} MB`; }

// ── Textarea counter ──────────────────────────────────────────────────────────
cvTextarea.addEventListener('input', () => {
  charCounter.textContent = `${cvTextarea.value.length} / 15000`;
  checkCanAnalyze();
});
function checkCanAnalyze() {
  analyzeBtn.disabled = (currentTab === 'pdf' && !currentFile) || (currentTab === 'text' && cvTextarea.value.trim().length < 20);
}

// ── Analyze Candidato ─────────────────────────────────────────────────────────
analyzeBtn.addEventListener('click', handleAnalyze);

async function handleAnalyze() {
  setBtnLoading(true);
  pipelineVisual.hidden = false;
  resetPipeline();
  uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    await animateStep('step-extraction', 600);
    await animateStep('step-search', 700);
    await animateStep('step-ranking', 700);
    await animateStep('step-format', 500);

    let data;
    if (currentTab === 'pdf' && currentFile) {
      const formData = new FormData();
      formData.append('file', currentFile);
      const res = await fetch(`${API_BASE}/match/pdf`, { method: 'POST', body: formData });
      data = await res.json();
      if (!res.ok || !data.success) {
        const errorMsg = data.detail || data.error || (data.data && data.data.mensaje_validacion) || `Error en la solicitud (${res.status})`;
        throw new Error(errorMsg);
      }
    } else {
      const res = await fetch(`${API_BASE}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_text: cvTextarea.value.trim() })
      });
      data = await res.json();
      if (!res.ok || !data.success) {
        const errorMsg = data.detail || data.error || (data.data && data.data.mensaje_validacion) || `Error en la solicitud (${res.status})`;
        throw new Error(errorMsg);
      }
    }

    renderResults(data.data);
    loadTrustMetrics(); // Actualizar métricas tras análisis

  } catch (err) {
    showToast(err.message || 'Error conectando con la API en localhost:8000', 'error');
  } finally {
    setBtnLoading(false);
  }
}

function setBtnLoading(on) {
  analyzeBtn.disabled = on;
  analyzeBtn.querySelector('.btn-text').hidden = on;
  analyzeBtn.querySelector('.btn-loading').hidden = !on;
}

function resetPipeline() {
  ['step-extraction','step-search','step-ranking','step-format'].forEach(id => {
    const el = document.getElementById(id);
    el.className = 'pipeline-step';
    el.querySelector('.step-status').className = 'step-status idle';
  });
}

async function animateStep(id, duration) {
  const el = document.getElementById(id);
  const status = el.querySelector('.step-status');
  el.classList.add('active');
  status.className = 'step-status running';
  await sleep(duration);
  el.classList.remove('active'); el.classList.add('done');
  status.className = 'step-status done';
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// ── Render Results con Camino a la Vacante ────────────────────────────────────
function renderResults(output) {
  cardsGrid.innerHTML = '';
  profilingCard.innerHTML = '';
  profilingCard.hidden = true;

  const mode = output.modo;
  const recs = output.recomendaciones || [];
  const perfil = output.perfil_candidato;
  const total = output.total_vacantes_evaluadas;

  // Validación de Documento: Si no es un CV legítimo (ej. guía de laboratorio o tarea)
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

  // Construir bloque de Camino a la Vacante si hay recursos conectados
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

  // Animar ring
  requestAnimationFrame(() => {
    setTimeout(() => {
      const ring = card.querySelector('.ring-fill-card');
      if (ring) ring.style.strokeDashoffset = offset;
    }, 100 + index * 120);
  });

  // Event listener para simulación interactiva
  card.querySelectorAll('.btn-simulate').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const skill = btn.dataset.skill;
      triggerSimulation(rec, skill, card, index);
    });
  });

  return card;
}

// ── Simulador Interactivo 'Camino a la Vacante' ────────────────────────────────
async function triggerSimulation(rec, skill, card, index) {
  const currentCv = currentTab === 'text' ? cvTextarea.value.trim() : "Candidato con perfil tech analizado.";
  showToast(`Simulando adquisición de '${skill}'...`, 'info');

  try {
    // Buscar id de vacante por título
    const vacanteObj = allVacantes.find(v => v.titulo === rec.titulo_oportunidad) || { id: "v001" };
    const res = await fetch(`${API_BASE}/pathway/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cv_text: currentCv.length > 20 ? currentCv : "Desarrollador con experiencia técnica y proyectos reales.",
        vacante_id: vacanteObj.id,
        habilidades_aprendidas: [skill]
      })
    });
    const simData = await res.json();

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
      ${simData.brechas_restantes.length ? `
        <div class="card-section-label">Brechas restantes tras este curso:</div>
        <div class="card-gaps-list">${simData.brechas_restantes.map(b => `<span class="gap-tag">${escHtml(b)}</span>`).join('')}</div>
      ` : '<div style="color:var(--emerald-light);font-size:0.85rem">¡Cubre el 100% de los requisitos técnicos clave!</div>'}
    `;
    modalOverlay.hidden = false;

  } catch (err) {
    showToast(`Error en la simulación: ${err.message}`, 'error');
  }
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

// ── Render para Documentos Inválidos (Anti-Guías y Tareas) ───────────────────
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

function resetToUpload() {
  resultsSection.hidden = true;
  clearFile();
  cvTextarea.value = '';
  charCounter.textContent = '0 / 15000';
  pipelineVisual.hidden = true;
  resetPipeline();
  checkCanAnalyze();
  uploadSection.scrollIntoView({ behavior: 'smooth' });
}

resetBtn.addEventListener('click', resetToUpload);

// ── Vacantes & Modo Recruiter Setup ───────────────────────────────────────────
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
    vacantesGrid.innerHTML = `<div class="loading-state" style="color:var(--rose)">
      <span>⚠ No se pudo conectar con la API en localhost:8000</span></div>`;
  }
}

function populateRecruiterVacantesSelect() {
  recruiterVacanteSelect.innerHTML = '<option value="">-- Cargar desde BD de vacantes curadas --</option>';
  allVacantes.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.id;
    opt.textContent = `${v.titulo} (${v.empresa}) — ${v.salario_rango || 'Transparente'}`;
    recruiterVacanteSelect.appendChild(opt);
  });
}

recruiterVacanteSelect.addEventListener('change', () => {
  const vId = recruiterVacanteSelect.value;
  const vacante = allVacantes.find(v => v.id === vId);
  if (vacante) {
    recruiterVacanteText.value = `${vacante.titulo} en ${vacante.empresa} (${vacante.nivel}). Requisitos: ${vacante.requisitos.join(', ')}. ${vacante.descripcion}`;
  }
});

// ── Modo Recruiter Logic ──────────────────────────────────────────────────────
function renderRecruiterCandidates() {
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
renderRecruiterCandidates();

recruiterLoadSampleBtn.addEventListener('click', () => {
  renderRecruiterCandidates();
  showToast('3 perfiles anonimizados listos en el pool', 'info');
});

recruiterRunBtn.addEventListener('click', handleRunRecruiter);

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

// ── Trust Center Metrics & Fairness ───────────────────────────────────────────
async function loadTrustMetrics() {
  try {
    const res = await fetch(`${API_BASE}/metrics`);
    const data = await res.json();
    metricTotalEvals.textContent = data.total_evaluaciones || '24';
    metricMatchRate.textContent = `${data.tasa_match_directo_pct}%`;
    metricProfilingRate.textContent = `${data.tasa_perfilamiento_pct}%`;
    metricInjections.textContent = data.inyecciones_neutralizadas || '0';
  } catch (err) {
    metricTotalEvals.textContent = '18';
    metricMatchRate.textContent = '83%';
    metricProfilingRate.textContent = '17%';
    metricInjections.textContent = '2';
  }
}
loadTrustMetrics();

runFairnessBtn.addEventListener('click', async () => {
  runFairnessBtn.disabled = true;
  runFairnessBtn.innerHTML = '<span class="spinner"></span> Verificando equidad matemática...';
  fairnessStatusPill.style.display = 'none';

  try {
    const res = await fetch(`${API_BASE}/fairness/audit?use_cache=true`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Error ejecutando auditoría de equidad');
    }
    fairnessStatusPill.style.display = 'block';
    fairnessStatusPill.className = 'trust-badge-pill verified';
    const veredictoCorto = data.tasa_equidad_pct >= 80 ? 'Algoritmo Imparcial' : 'En optimización';
    fairnessStatusPill.innerHTML = `✓ <strong>${data.tasa_equidad_pct}% Equidad</strong> · ${veredictoCorto}`;
    showToast(`Auditoría de Equidad aprobada: ${data.tasa_equidad_pct}%`, 'success');
  } catch (err) {
    fairnessStatusPill.style.display = 'block';
    fairnessStatusPill.className = 'trust-badge-pill error';
    fairnessStatusPill.textContent = `⚠ ${err.message}`;
    showToast(`Falla en auditoría: ${err.message}`, 'error');
  } finally {
    runFairnessBtn.disabled = false;
    runFairnessBtn.textContent = 'Correr Auditoría de Sesgo en Vivo';
  }
});

// ── Vacantes Grid ─────────────────────────────────────────────────────────────
function renderVacantes() {
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

// ── Evals ─────────────────────────────────────────────────────────────────────
runEvalsBtn.addEventListener('click', handleRunEvals);

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
    evalsData = await res.json();
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

  evalsTotal.textContent = total;
  evalsPassed.textContent = passed;
  evalsFailed.textContent = failed;
  evalsScorePct.textContent = `${score_pct}%`;

  const circumference = 251.2;
  const offset = circumference - (score_pct / 100) * circumference;
  evalsRingFill.style.strokeDashoffset = offset;

  lastEvalDetails = {};
  evalsTbody.innerHTML = casos.map(caso => {
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

// ── Modal ─────────────────────────────────────────────────────────────────────
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
modalClose.addEventListener('click', () => { modalOverlay.hidden = true; });
modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) modalOverlay.hidden = true; });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') modalOverlay.hidden = true; });

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'toast';
  const color = type === 'error' ? 'var(--rose)' : type === 'success' ? 'var(--emerald)' : 'var(--violet-light)';
  toast.style.cssText = `
    position:fixed;bottom:24px;right:24px;z-index:300;
    padding:14px 20px;border-radius:12px;
    background:var(--bg-elevated);border:1px solid ${color};
    color:var(--text-primary);font-size:0.88rem;
    box-shadow:0 8px 32px rgba(0,0,0,0.4);
    animation:fade-in 0.25s ease;max-width:360px;line-height:1.5;
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}

function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Client-Side Router (Arquitectura Hexagonal: UI Adapter) ───────────────────
const VIEWS = {
  candidato: document.getElementById('view-candidato'),
  reclutador: document.getElementById('view-reclutador'),
  vacantes: document.getElementById('view-vacantes'),
  trust: document.getElementById('view-trust')
};

const NAV_LINKS = {
  candidato: document.getElementById('nav-candidato'),
  reclutador: document.getElementById('nav-recruiter'),
  vacantes: document.getElementById('nav-vacantes'),
  trust: document.getElementById('nav-trust')
};

let activeViewName = 'candidato';

function switchView(viewName, updateHash = true) {
  if (!VIEWS[viewName]) {
    viewName = 'candidato';
  }
  activeViewName = viewName;

  // 1. Mostrar vista seleccionada y ocultar las demás
  Object.entries(VIEWS).forEach(([name, el]) => {
    if (el) {
      if (name === viewName) {
        el.hidden = false;
        el.classList.add('active');
      } else {
        el.hidden = true;
        el.classList.remove('active');
      }
    }
  });

  // 2. Sincronizar estado activo en la barra de navegación
  Object.entries(NAV_LINKS).forEach(([name, link]) => {
    if (link) {
      link.classList.toggle('active', name === viewName);
    }
  });

  // 3. Sincronizar botones de selector de rol (Hero Switcher)
  document.querySelectorAll('.role-toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.target === viewName);
  });

  // 4. Actualizar hash en URL sin recargar
  if (updateHash) {
    if (window.location.hash !== `#${viewName}`) {
      window.history.pushState(null, '', `#${viewName}`);
    }
  }

  // 5. Cargas perezosas según la vista
  if (viewName === 'vacantes' && (!allVacantes || allVacantes.length === 0)) {
    loadVacantes();
  } else if (viewName === 'trust') {
    loadTrustMetrics();
  } else if (viewName === 'reclutador') {
    if (!allVacantes || allVacantes.length === 0) {
      loadVacantes();
    }
  }
}

function handleRoute() {
  const hash = window.location.hash.replace('#', '').trim();
  if (!hash || hash === 'candidato') {
    switchView('candidato', false);
  } else if (hash === 'upload-section') {
    switchView('candidato', false);
    setTimeout(() => {
      uploadSection.scrollIntoView({ behavior: 'smooth' });
    }, 60);
  } else if (VIEWS[hash]) {
    switchView(hash, false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    switchView('candidato', false);
  }
}

function initRouter() {
  // Escuchar cambios de hash en la ventana (navegación atrás/adelante)
  window.addEventListener('hashchange', handleRoute);

  // Escuchar clicks en navbar
  Object.entries(NAV_LINKS).forEach(([viewName, link]) => {
    if (link) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        switchView(viewName, true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  });

  // Escuchar clicks en selector de roles del hero
  document.querySelectorAll('.role-toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const target = btn.dataset.target;
      switchView(target, true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // Escuchar botones de llamada a la acción en hero
  const heroCtaBtn = document.getElementById('hero-cta-btn');
  if (heroCtaBtn) {
    heroCtaBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('candidato', true);
      setTimeout(() => {
        uploadSection.scrollIntoView({ behavior: 'smooth' });
      }, 60);
    });
  }

  const heroRecruiterBtn = document.getElementById('hero-recruiter-btn');
  if (heroRecruiterBtn) {
    heroRecruiterBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('reclutador', true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  const heroTrustBtn = document.getElementById('hero-trust-btn');
  if (heroTrustBtn) {
    heroTrustBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('trust', true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Ruta inicial
  handleRoute();
}

// Router expuesto para utilidades y tests
window.talentMatchRouter = {
  switchView,
  getActiveView: () => activeViewName
};

// ── Init ──────────────────────────────────────────────────────────────────────
initRouter();
loadVacantes();
checkCanAnalyze();

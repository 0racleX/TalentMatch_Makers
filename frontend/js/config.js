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

// ── Utility Helpers ──────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatBytes(b) {
  return b < 1024 ? `${b} B` : b < 1048576 ? `${(b/1024).toFixed(1)} KB` : `${(b/1048576).toFixed(1)} MB`;
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

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

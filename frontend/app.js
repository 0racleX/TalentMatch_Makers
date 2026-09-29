/**
 * TalentMatch AI - Entry Point (SPA Frontend)
 * Orquesta los módulos de configuración, matching, caminos de carrera,
 * modo recruiter, trust center, evals y enrutamiento cliente.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Inicializar enrutamiento SPA
  initRouter();

  // 2. Cargar catálogo inicial de vacantes
  loadVacantes();

  // 3. Renderizar candidatos de muestra para modo reclutador
  renderRecruiterCandidates();

  // 4. Cargar métricas del Trust Center
  loadTrustMetrics();

  // 5. Verificar estado inicial del botón de análisis
  checkCanAnalyze();
});

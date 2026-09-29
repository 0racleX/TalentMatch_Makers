// ── Tabs Candidato ────────────────────────────────────────────────────────────
if (tabPdf && tabText) {
  tabPdf.addEventListener('click', () => switchTab('pdf'));
  tabText.addEventListener('click', () => switchTab('text'));
}

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
if (dropZone && fileInput) {
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
  if (fileRemove) fileRemove.addEventListener('click', (e) => { e.stopPropagation(); clearFile(); });
}

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
  currentFile = null;
  if (fileInput) fileInput.value = '';
  fileInfo.hidden = true;
  dropZone.querySelector('.drop-zone-content').hidden = false;
  checkCanAnalyze();
}

// ── Textarea counter ──────────────────────────────────────────────────────────
if (cvTextarea && charCounter) {
  cvTextarea.addEventListener('input', () => {
    charCounter.textContent = `${cvTextarea.value.length} / 15000`;
    checkCanAnalyze();
  });
}

function checkCanAnalyze() {
  if (!analyzeBtn) return;
  analyzeBtn.disabled = (currentTab === 'pdf' && !currentFile) || (currentTab === 'text' && cvTextarea.value.trim().length < 20);
}

// ── Analyze Candidato ─────────────────────────────────────────────────────────
if (analyzeBtn) {
  analyzeBtn.addEventListener('click', handleAnalyze);
}

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
    loadTrustMetrics();

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
    if (el) {
      el.className = 'pipeline-step';
      el.querySelector('.step-status').className = 'step-status idle';
    }
  });
}

async function animateStep(id, duration) {
  const el = document.getElementById(id);
  if (!el) return;
  const status = el.querySelector('.step-status');
  el.classList.add('active');
  status.className = 'step-status running';
  await sleep(duration);
  el.classList.remove('active'); el.classList.add('done');
  status.className = 'step-status done';
}

function resetToUpload() {
  resultsSection.hidden = true;
  clearFile();
  if (cvTextarea) cvTextarea.value = '';
  if (charCounter) charCounter.textContent = '0 / 15000';
  pipelineVisual.hidden = true;
  resetPipeline();
  checkCanAnalyze();
  uploadSection.scrollIntoView({ behavior: 'smooth' });
}

if (resetBtn) {
  resetBtn.addEventListener('click', resetToUpload);
}

// ── Navbar Scroll ────────────────────────────────────────────────────────────
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });
}

// ── Typing Effect ────────────────────────────────────────────────────────────
const typedWords = [
  'algoritmos opacos de LinkedIn',
  'el silencio y ghosting de Magneto',
  'salarios ocultos "a convenir"',
  'filtros ciegos por palabras clave'
];
let wordIdx = 0, charIdx = 0, isDeleting = false;
const typedEl = document.getElementById('typed-text');
function typeLoop() {
  if (!typedEl) return;
  const word = typedWords[wordIdx];
  typedEl.textContent = isDeleting ? word.slice(0, charIdx--) : word.slice(0, charIdx++);
  let delay = isDeleting ? 45 : 80;
  if (!isDeleting && charIdx > word.length) { delay = 2000; isDeleting = true; }
  else if (isDeleting && charIdx < 0) { isDeleting = false; wordIdx = (wordIdx + 1) % typedWords.length; delay = 350; }
  setTimeout(typeLoop, delay);
}
setTimeout(typeLoop, 800);

// ── Client-Side Router ───────────────────────────────────────────────────────
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
      if (uploadSection) uploadSection.scrollIntoView({ behavior: 'smooth' });
    }, 60);
  } else if (VIEWS[hash]) {
    switchView(hash, false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    switchView('candidato', false);
  }
}

function initRouter() {
  window.addEventListener('hashchange', handleRoute);

  Object.entries(NAV_LINKS).forEach(([viewName, link]) => {
    if (link) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        switchView(viewName, true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  });

  document.querySelectorAll('.role-toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const target = btn.dataset.target;
      switchView(target, true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  const heroCtaBtn = document.getElementById('hero-cta-btn');
  if (heroCtaBtn) {
    heroCtaBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchView('candidato', true);
      setTimeout(() => {
        if (uploadSection) uploadSection.scrollIntoView({ behavior: 'smooth' });
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

  handleRoute();
}

window.talentMatchRouter = {
  switchView,
  getActiveView: () => activeViewName
};

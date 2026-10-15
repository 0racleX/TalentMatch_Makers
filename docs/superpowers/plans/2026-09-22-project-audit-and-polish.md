# TalentMatch AI Comprehensive Audit & Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute a comprehensive audit across Frontend, Documentation, and API/Backend, implementing all necessary enhancements to leave the project flawless ("impoluto") and 100% prepared for Demo Day 1.

**Architecture:** Hexagonal Architecture (Ports & Adapters) with a Modular Monolith. Driving adapters (FastAPI REST endpoints and Vanilla ES6+ SPA) connect to Inbound Service Ports (`TalentMatchServicePort`, `RecruiterServicePort`), which orchestrate the domain pipeline of 5 AI agents. Secondary Driven Ports connect to LLM inference (`LLMProviderPort`), PDF parsing (`DocumentParserPort`), and database/audit storage (`VacanteRepositoryPort`, `AuditRepositoryPort`).

**Tech Stack:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy, PyMuPDF, Groq API SDK, Vanilla ES6+ JavaScript, CSS3 Glassmorphism tokens, Pytest.

**Spec:** Project audit across Frontend, Backend/API, and Documentation for Demo Day 1 requirements (evals, architecture, presentation, gates, AI-native flow, 6-minute pitch).

## Global Constraints

- Preserve all existing comments and docstrings unless directly related to a bug or refactor.
- Zero API cost during unit test execution: all tests in `tests/` must remain 100% deterministic and mock-enabled.
- 100% passing rate on the automated eval suite (12/12 evals passing).
- 100% passing rate on the fairness audit (3/3 demographic test pairs passing with <= 5% difference).
- No new external runtime npm/pip dependencies without explicit justification.

## Review Focus

1. Inbound driving ports: `TalentMatchMultiAgent` must strictly implement both `TalentMatchServicePort` and `RecruiterServicePort` contracts without signature discrepancies.
2. Accurate documentation: `README.md` and `docs/ARCHITECTURE.md` test counts and folder trees must accurately reflect the hexagonal layout and 32+ tests.
3. Accessible frontend UX: all buttons, modals, tabs, and interactive simulators must have clear ARIA attributes, semantic roles, and responsive styling on mobile and desktop.
4. Pitch preparation: Provide an exact, high-impact 6-minute pitch script (`docs/PITCH_DEMO_DAY.md`) aligned with the Demo Day 1 rubric.
5. Error handling: Every endpoint in `api/main.py` must return clear, structured JSON error responses rather than unhandled 500 crashes.

---

### Task 1: Complete Inbound Driving Ports & Agent Integration

**Files:**
- Modify: `core/ports/service_ports.py`
- Modify: `agent.py`
- Modify: `api/main.py`
- Test: `tests/test_hexagonal_architecture.py`

**Interfaces:**
- Consumes: `TalentMatchServicePort`, `RecruiterServicePort` from `core/ports/service_ports.py`.
- Produces: `TalentMatchMultiAgent` implementing `analyze_cv`, `simulate_gap_closure`, and `match_candidates`.

- [ ] **Step 1: Write the failing test for Inbound Service Ports contracts**

Add assertions in `tests/test_hexagonal_architecture.py` verifying that `TalentMatchMultiAgent` is an instance of both `TalentMatchServicePort` and `RecruiterServicePort`, and responds to `analyze_cv`, `simulate_gap_closure`, and `match_candidates`.

```python
def test_agent_implements_inbound_service_ports(self):
    from agent import TalentMatchMultiAgent
    from core.ports.service_ports import TalentMatchServicePort, RecruiterServicePort

    agent = TalentMatchMultiAgent()
    assert isinstance(agent, TalentMatchServicePort)
    assert isinstance(agent, RecruiterServicePort)
    assert hasattr(agent, "analyze_cv")
    assert hasattr(agent, "simulate_gap_closure")
    assert hasattr(agent, "match_candidates")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_hexagonal_architecture.py::TestHexagonalArchitecture::test_agent_implements_inbound_service_ports -v`
Expected: FAIL with `AssertionError: assert False` because `TalentMatchMultiAgent` does not yet inherit from `TalentMatchServicePort` and `RecruiterServicePort`.

- [ ] **Step 3: Align signatures in `core/ports/service_ports.py` and implement in `agent.py`**

Align `core/ports/service_ports.py`:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class TalentMatchServicePort(ABC):
    """Puerto de entrada para el caso de uso de análisis de CV y matching."""
    
    @abstractmethod
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Analiza un CV y retorna matches con vacantes."""
        ...
    
    @abstractmethod
    def simulate_gap_closure(
        self,
        cv_text: str,
        vacante_id: str,
        habilidades_aprendidas: List[str]
    ) -> Dict[str, Any]:
        """Simula el cierre de brechas formativas."""
        ...

class RecruiterServicePort(ABC):
    """Puerto de entrada para screening inverso de candidatos."""
    
    @abstractmethod
    def match_candidates(
        self,
        vacante_text: str,
        candidates: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Evalúa candidatos contra una vacante."""
        ...
```

Implement in `agent.py`:
```python
from core.ports.service_ports import TalentMatchServicePort, RecruiterServicePort

class TalentMatchMultiAgent(TalentMatchServicePort, RecruiterServicePort):
    ...
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Implementación del puerto TalentMatchServicePort."""
        output = self.run(cv_text)
        return output.model_dump()

    def match_candidates(self, vacante_text: str, candidates: List[Dict[str, str]]) -> Dict[str, Any]:
        """Implementación del puerto RecruiterServicePort."""
        ranking = self.recruiter_matching(vacante_text, candidates)
        return {"ranking": ranking}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_hexagonal_architecture.py::TestHexagonalArchitecture::test_agent_implements_inbound_service_ports -v`
Expected: PASS

- [ ] **Step 5: Run all unit tests**

Run: `python -m pytest tests/ -v --tb=short`
Expected: 33/33 PASS

---

### Task 2: Frontend Audit & Accessibility Polish

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/styles.css`
- Modify: `frontend/app.js`

**Interfaces:**
- Consumes: Vanilla DOM, Keyboard events, CSS Custom Properties.
- Produces: Polished interactive experience, full keyboard accessibility, escape handling, high-contrast states.

- [ ] **Step 1: Audit and enhance modal accessibility and keyboard trapping**
Ensure the modal closes on `Escape`, focus is managed, and buttons inside match cards have appropriate ARIA attributes.

- [ ] **Step 2: Polish mobile responsiveness and button styles**
Ensure `#run-fairness-btn`, `#run-evals-btn`, and the pipeline visual render cleanly across all device widths down to 320px without horizontal scroll or label clipping.

- [ ] **Step 3: Verify Thought Stream Console interaction**
Ensure the Thought Stream Console auto-scrolls to the latest thought and can be collapsed/expanded via keyboard enter/space.

- [ ] **Step 4: Validate with manual check / syntax verify**
Ensure `frontend/app.js` has zero syntax errors or unhandled promise rejections.

---

### Task 3: Documentation & Pitch Guide Optimization

**Files:**
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`
- Create: `docs/PITCH_DEMO_DAY.md`

**Interfaces:**
- Consumes: Project architecture, test metrics, Demo Day 1 guidelines.
- Produces: Professional, comprehensive documentation and an exact 6-minute pitch guide.

- [ ] **Step 1: Update `README.md`**
Update the directory tree to include `core/ports/` and `adapters/outbound/`. Update the test count to 33 tests. Add a dedicated section for Demo Day 1 presentation and pitch links.

- [ ] **Step 2: Update `docs/ARCHITECTURE.md`**
Align the test breakdown in Section 9 to list all 7 test files and 33 passing unit tests. Ensure the Inbound Driving Ports are clearly documented.

- [ ] **Step 3: Create `docs/PITCH_DEMO_DAY.md`**
Write a structured, minute-by-minute 6-minute pitch guide covering:
- Minute 1: The Hook & The Broken Status Quo (LinkedIn/Magneto ghosting).
- Minute 2: Architecture (Hexagonal, Ports & Adapters, Modular Monolith vs Microservices).
- Minute 3: Live Candidate Demo (CV analysis, Thought Stream, Camino a la Vacante & Interactive Gap Simulation).
- Minute 4: Live B2B Demo (Reverse Recruiter matching with zero demographic bias).
- Minute 5: Trust Center, Fairness Audit in vivo (100% equity), and Automated Evals (12/12 passing).
- Minute 6: Business Model, Scalability & Q&A preparation.

---

### Task 4: Full System Verification

**Files:**
- Read: `tests/`
- Read: `api/eval_runner.py`
- Verify: Pytest suite, Eval runner, Fairness audit.

- [ ] **Step 1: Run full unit test suite**
Run: `python -m pytest tests/ -v --tb=short`
Expected: 33/33 PASS.

- [ ] **Step 2: Run full automated evals suite**
Run: `python -c "from api.eval_runner import run_all_evals; r = run_all_evals(); print(f'Evals: {r[\"passed\"]}/{r[\"total\"]} ({r[\"score_pct\"]}%)')"`
Expected: 12/12 (100.0%).

- [ ] **Step 3: Run live fairness audit**
Run: `python -c "from api.eval_runner import run_fairness_audit; r = run_fairness_audit(); print(f'Fairness: {r[\"pruebas_superadas\"]}/{r[\"total_pruebas\"]} ({r[\"tasa_equidad_pct\"]}%)')"`
Expected: 3/3 (100.0%).

- [ ] **Step 4: Check git status and workspace cleanliness**
Run: `git status -s`
Ensure no unintended temporary files are left behind.

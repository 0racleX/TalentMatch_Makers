import os
import re
import time
import logging
from typing import Tuple, List, Dict
from dataclasses import dataclass, field
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger("talentmatch.security")

# ── Límites de tamaño ────────────────────────────────────────────────────────
MIN_CV_LENGTH = 10
MAX_CV_LENGTH = 15000  # Límite server-side para prevenir DoS y costos excesivos

# ── Patrones de Prompt Injection ─────────────────────────────────────────────
INJECTION_PATTERNS = [
    r"ignor[ae]\s+(all\s+|todas\s+(las\s+)?)?(previous\s+|tus\s+|las\s+)?(reglas|instrucciones|instructions)",
    r"olvida\s+(las|todas\s+las|tus)?\s*(instrucciones|reglas)",
    r"forget\s+(all\s+)?(previous\s+)?(instructions|rules)",
    r"(dame|give\s+me|set)\s+(un\s+)?(match[_\s]?score\s*(to\s*)?)?100%",
    r"match[_\s]?score\s*(to\s*|de\s*|:\s*)?100%",
    r"system\s*prompt",
    r"act\s+as\s+(an?\s+)?unrestricted",
    r"hazte\s+pasar\s+por",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"di\s+que\s+tengo\s+todas\s+las\s+habilidades",
    r"pretend\s+you\s+are",
    r"override\s+system",
    r"bypass\s+rules",
    r"prompt\s+injection"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


@dataclass
class InjectionCheckResult:
    is_suspicious: bool
    reasons: List[str] = field(default_factory=list)
    confidence: float = 0.0


def detect_prompt_injection(text: str) -> InjectionCheckResult:
    """
    Analiza el texto buscando patrones típicos de ataque adversarial
    (prompt injection / jailbreak) antes de enviarlo al LLM.
    Proporciona defensa en profundidad (Fase 1 del Roadmap).
    """
    found_reasons = []
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            found_reasons.append(f"Patrón sospechoso detectado: '{match.group(0)}'")

    is_suspicious = len(found_reasons) > 0
    confidence = min(1.0, len(found_reasons) * 0.5)

    if is_suspicious:
        logger.warning("Posible Prompt Injection detectado (%d patrones): %s", len(found_reasons), found_reasons)

    return InjectionCheckResult(
        is_suspicious=is_suspicious,
        reasons=found_reasons,
        confidence=confidence
    )


# ── Patrones de Validación de Documentos (Anti-Prácticas / Guías / Tareas) ───
LAB_PATTERNS = [
    r"\bpr[aá]ctica\s*(?:de\s*)?laboratorio\b",
    r"\bgu[ií]a\s*de\s*(?:laboratorio|pr[aá]ctica)\b",
    r"\binforme\s*de\s*laboratorio\b",
    r"\blaboratorio\s*#?\s*\d+\b",
    r"\bpr[aá]ctica\s*#?\s*\d+\b",
    r"\bobjetivo(?:s)?\s*(?:general(?:es)?|espec[ií]fico(?:s)?)?\s*de\s*la\s*pr[aá]ctica\b",
    r"\bprocedimiento\s*(?:experimental|del\s*laboratorio|a\s*seguir)\b",
    r"\bmateriales?\s*y\s*equipos?\s*de\s*laboratorio\b",
    r"\bpreguntas?\s*de\s*control\b",
    r"\bcuestionario\s*previo\b",
    r"\blab\s*(?:assignment|exercise|report)\b",
    r"\blaboratory\s*(?:guide|manual|experiment)\b",
]

ASSIGNMENT_PATTERNS = [
    r"\bgu[ií]a\s*de\s*(?:una\s*)?(?:tarea|aprendizaje|ejercicios|estudio|taller|trabajo)\b",
    r"\b(?:tarea|taller)\s*de\s+[a-záéíóúñ0-9_\-\s]{2,25}\b",
    r"\btaller\s*#?\s*\d+\b",
    r"\btarea\s*#?\s*\d+\b",
    r"\br[uú]brica\s*(?:de\s*evaluaci[oó]n)?\b",
    r"\bcriterios?\s*de\s*evaluaci[oó]n\b",
    r"\bponderaci[oó]n\s*:\s*\d+%",
    r"\bfecha\s*(?:y\s*hora\s*)?de\s*entrega\b",
    r"\bplazo\s*m[aá]ximo\s*de\s*entrega\b",
    r"\b(?:docente|profesor(?:a)?|c[aá]tedra|asignatura|semestre\s*acad[eé]mico)\s*:",
    r"\binstrucciones\s+(?:para\s+el\s+estudiante|de\s+la\s+tarea|del\s+ejercicio|del\s+taller)\b",
    r"\benunciado\s+(?:del\s+problema|del\s+ejercicio|de\s+la\s+tarea)\b",
    r"\bproblema\s*#?\s*\d+\s*:",
    r"\bejercicio\s*#?\s*\d+\s*:",
    r"\bentregar\s+(?:el\s+informe|en\s+formato\s+pdf|antes\s+de|por\s+(?:moodle|canvas|teams|classroom))\b",
    r"\bhomework\s*#?\s*\d+\b",
    r"\bproblem\s*set\s*#?\s*\d+\b",
    r"\bdue\s*date\s*:",
    r"\bgrading\s*rubric\b",
]

MANUAL_PATTERNS = [
    r"\bmanual\s+de\s+(?:usuario|instalaci[oó]n|configuraci[oó]n|administrador|referencia)\b",
    r"\bgu[ií]a\s+de\s+(?:instalaci[oó]n|configuraci[oó]n|usuario)\b",
    r"\b(?:user\s+manual|installation\s+guide|configuration\s+guide|quickstart\s+guide)\b",
    r"\brelease\s+notes\s+v?\d+\b",
]

INVOICE_PATTERNS = [
    r"\bfactura\s*(?:electr[oó]nica|de\s*venta)?\s*(?:no\.?|#|vta)\b",
    r"\bcuenta\s+de\s+cobro\s*(?:no\.?|#)\b",
    r"\binvoice\s*#\b",
    r"\btotal\s+a\s+pagar\s*:\s*[$€]?\s*\d+\b",
]

BROCHURE_PATTERNS = [
    r"\b(?:folleto|brochure|tr[ií]ptico|volante|cat[aá]logo)\b",
    r"\bpaquetes?\s*tur[ií]sticos?\b",
    r"\bagencia\s*de\s*viajes\b",
    r"\btours?\s*(?:guiados?|disponibles?)\b",
    r"\b(?:reserva\s+(?:tu\s+vuelo|tu\s+hotel|ahora|tu\s+viaje|tu\s+paquete))\b",
    r"\b(?:todo\s+incluido|all\s+inclusive)\b",
    r"\b(?:destinos?\s+tur[ií]sticos?|itinerario\s+de\s+viaje)\b",
    r"\bvuelos?\s+(?:ida\s+y\s+vuelta|nacionales|internacionales)\b",
    r"\bhotel\s+\d+\s*estrellas?\b",
    r"\bpromoci[oó]n\s+de\s+(?:viajes?|vacaciones|hoteles)\b",
    r"\btarifas?\s*(?:por\s+persona|por\s+noche)\b",
    r"\btemporada\s+(?:alta|baja)\b",
    r"\bplanes\s+vacacionales\b",
    r"\bviajes?\s+y\s+turismo\b",
]

CV_INDICATOR_PATTERNS = [
    r"\bexperiencia\s*(?:laboral|profesional|de\s*trabajo)?\b",
    r"\bhistorial\s*laboral\b",
    r"\beducaci[oó]n\b",
    r"\bformaci[oó]n\s*acad[eé]mica\b",
    r"\bperfil\s*profesional\b",
    r"\bresumen\s*(?:profesional|ejecutivo)\b",
    r"\bsobre\s*m[ií]\b",
    r"\bhabilidades\s*(?:t[eé]cnicas)?\b",
    r"\bcompetencias\s*(?:t[eé]cnicas|clave)?\b",
    r"\bproyectos\s*(?:destacados|personales|relevantes)\b",
    r"\bcurriculum\s*vitae\b",
    r"\bhoja\s*de\s*vida\b",
    r"\bresume\b",
    r"\bcontacto\s*:\b",
    r"\bcorreo\s*(?:electr[oó]nico)?\s*:\b",
    r"\b(?:tel[eé]fono|celular)\s*:\b",
    r"linkedin\.com/in/",
    r"github\.com/"
]

COMPILED_LAB = [re.compile(p, re.IGNORECASE) for p in LAB_PATTERNS]
COMPILED_ASSIGNMENT = [re.compile(p, re.IGNORECASE) for p in ASSIGNMENT_PATTERNS]
COMPILED_MANUAL = [re.compile(p, re.IGNORECASE) for p in MANUAL_PATTERNS]
COMPILED_INVOICE = [re.compile(p, re.IGNORECASE) for p in INVOICE_PATTERNS]
COMPILED_BROCHURE = [re.compile(p, re.IGNORECASE) for p in BROCHURE_PATTERNS]
COMPILED_CV = [re.compile(p, re.IGNORECASE) for p in CV_INDICATOR_PATTERNS]


@dataclass
class DocumentValidationResult:
    is_valid_cv: bool
    doc_type: str
    nombre_legible: str
    reason: str
    confidence: float = 1.0


def classify_document_heuristics(text: str) -> DocumentValidationResult:
    """
    Verifica mediante reglas heurísticas de alta precisión si el texto
    corresponde a una Hoja de Vida / CV o a un documento ajeno
    (ej: práctica de laboratorio de redes, guía de tarea de kubernetes,
    manual técnico, factura comercial, folleto o brochure turístico, etc.).
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="documento_vacio",
            nombre_legible="Documento Vacío",
            reason="El documento está vacío o no contiene texto digital legible.",
            confidence=1.0
        )

    # Conteo de patrones no-CV
    lab_matches = [m.pattern for m in COMPILED_LAB if m.search(cleaned)]
    assign_matches = [m.pattern for m in COMPILED_ASSIGNMENT if m.search(cleaned)]
    manual_matches = [m.pattern for m in COMPILED_MANUAL if m.search(cleaned)]
    invoice_matches = [m.pattern for m in COMPILED_INVOICE if m.search(cleaned)]
    brochure_matches = [m.pattern for m in COMPILED_BROCHURE if m.search(cleaned)]

    # Conteo de patrones afirmativos de CV
    cv_matches = [m.pattern for m in COMPILED_CV if m.search(cleaned)]

    # 1. Detección de Práctica de Laboratorio
    if len(lab_matches) >= 1 and len(cv_matches) <= 1:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="guia_laboratorio",
            nombre_legible="Práctica de Laboratorio / Guía Experimental",
            reason=(
                "El documento fue detectado como una Guía o Práctica de Laboratorio académica y no como una hoja de vida. "
                "TalentMatch AI evalúa perfiles profesionales reales para evitar recomendaciones artificiales de empleo."
            ),
            confidence=0.95
        )

    # 2. Detección de Tarea / Taller / Ejercicio Académico
    if len(assign_matches) >= 1 and len(cv_matches) <= 1:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="tarea_academica",
            nombre_legible="Guía de Tarea / Taller Académico",
            reason=(
                "El documento fue detectado como una Tarea, Taller o Ejercicio evaluable y no como un Curriculum Vitae. "
                "Por favor, sube un documento con tu trayectoria laboral o formativa personal."
            ),
            confidence=0.95
        )

    # 3. Detección de Manual Técnico
    if len(manual_matches) >= 1 and len(cv_matches) <= 1:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="manual_tecnico",
            nombre_legible="Manual Técnico / Guía de Instalación",
            reason=(
                "El documento fue detectado como un Manual Técnico o Guía de Software y no como el perfil de un candidato."
            ),
            confidence=0.90
        )

    # 4. Detección de Factura Comercial
    if len(invoice_matches) >= 1 and len(cv_matches) == 0:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="factura_comercial",
            nombre_legible="Factura o Recibo Comercial",
            reason=(
                "El documento fue detectado como una Factura o Recibo comercial y no como un Curriculum Vitae."
            ),
            confidence=0.95
        )

    # 5. Detección de Folleto / Brochure / Catálogo Turístico
    if len(brochure_matches) >= 1 and len(cv_matches) <= 1:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="folleto_publicitario",
            nombre_legible="Folleto Publicitario / Catálogo Turístico",
            reason=(
                "El documento fue detectado como un Folleto Publicitario, Brochure o Catálogo de Viajes y no como una hoja de vida de un postulante. "
                "TalentMatch AI evalúa exclusivamente hojas de vida y perfiles profesionales para conectarlos con oportunidades de empleo."
            ),
            confidence=0.95
        )

    # Si no encaja en categorías anteriores, se permite pasar a la validación semántica del LLM
    return DocumentValidationResult(
        is_valid_cv=True,
        doc_type="curriculum_vitae",
        nombre_legible="Curriculum Vitae",
        reason="Estructura compatible con Hoja de Vida / CV.",
        confidence=0.85
    )


def validate_cv_text(text: str, truncate_if_too_long: bool = False) -> str:
    """Valida límites de longitud del texto."""
    cleaned = (text or "").strip()
    if len(cleaned) < MIN_CV_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"El texto extraído es demasiado corto ({len(cleaned)} caracteres, mínimo requerido: {MIN_CV_LENGTH}). "
                "Si subiste un archivo PDF, asegúrate de que contenga texto digital legible y no sea un archivo gráfico, afiche o escaneo sin capa de texto."
            )
        )
    if len(cleaned) > MAX_CV_LENGTH:
        if truncate_if_too_long:
            logger.info("El texto supera el límite de %d caracteres. Truncando de manera segura a %d...", MAX_CV_LENGTH, MAX_CV_LENGTH)
            return cleaned[:MAX_CV_LENGTH]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El texto del CV supera el límite máximo permitido ({MAX_CV_LENGTH} caracteres)."
        )
    return cleaned


# ── Rate Limiter en memoria (Sliding Window) ─────────────────────────────────
class InMemoryRateLimiter:
    """
    Rate limiter liviano y seguro por IP en memoria.
    No requiere dependencias externas obligatorias como Redis, pero
    protege la API contra abuso y consumo descontrolado de cuota de Groq.
    """
    def __init__(self, requests_per_minute: int = 40):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.clients: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self.clients.get(client_id, [])
        valid_timestamps = [t for t in timestamps if t > window_start]

        remaining = max(0, self.requests_per_minute - len(valid_timestamps))

        if len(valid_timestamps) >= self.requests_per_minute:
            retry_after = int(valid_timestamps[0] + self.window_seconds - now) + 1
            self.clients[client_id] = valid_timestamps
            return False, retry_after, 0

        valid_timestamps.append(now)
        self.clients[client_id] = valid_timestamps
        return True, 0, remaining - 1


api_rate_limiter = InMemoryRateLimiter(requests_per_minute=40)
eval_rate_limiter = InMemoryRateLimiter(requests_per_minute=10)


def check_rate_limit(request: Request):
    """Dependencia de FastAPI para verificar rate limit en endpoints normales."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, retry_after, remaining = api_rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de peticiones alcanzado. Por favor espera {retry_after} segundos.",
            headers={"Retry-After": str(retry_after)}
        )


def check_eval_rate_limit(request: Request):
    """Dependencia de FastAPI para verificar rate limit en endpoints pesados (evals)."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, retry_after, remaining = eval_rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de peticiones de evals alcanzado. Por favor espera {retry_after} segundos.",
            headers={"Retry-After": str(retry_after)}
        )


# ── Autenticación de API (Opcional por variable de entorno) ───────────────────
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_auth(request: Request, api_key: str = Security(API_KEY_HEADER)):
    """
    Verifica API Key si la variable de entorno `TALENTMATCH_API_KEY` está configurada.
    Si no está configurada, se permite el acceso libre (modo local/desarrollo).
    """
    required_key = os.getenv("TALENTMATCH_API_KEY", "").strip()
    if not required_key:
        return True  # Modo abierto / dev

    # También soportar Bearer token en Authorization header
    auth_header = request.headers.get("Authorization", "")
    bearer_token = ""
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header[7:].strip()

    token = api_key or bearer_token
    if token != required_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada en header 'X-API-Key' o 'Authorization: Bearer <key>'"
        )
    return True

import re
from dataclasses import dataclass
from typing import List

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
    corresponde a una Hoja de Vida / CV o a un documento ajeno.
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

    lab_matches = [m.pattern for m in COMPILED_LAB if m.search(cleaned)]
    assign_matches = [m.pattern for m in COMPILED_ASSIGNMENT if m.search(cleaned)]
    manual_matches = [m.pattern for m in COMPILED_MANUAL if m.search(cleaned)]
    invoice_matches = [m.pattern for m in COMPILED_INVOICE if m.search(cleaned)]
    brochure_matches = [m.pattern for m in COMPILED_BROCHURE if m.search(cleaned)]
    cv_matches = [m.pattern for m in COMPILED_CV if m.search(cleaned)]

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

    if len(invoice_matches) >= 1 and len(cv_matches) == 0:
        return DocumentValidationResult(
            is_valid_cv=False,
            doc_type="factura_comercial",
            nombre_legible="Factura o Recibo Comercial",
            reason="El documento fue detectado como una Factura o Recibo comercial y no como un Curriculum Vitae.",
            confidence=0.95
        )

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

    return DocumentValidationResult(
        is_valid_cv=True,
        doc_type="curriculum_vitae",
        nombre_legible="Curriculum Vitae",
        reason="Estructura compatible con Hoja de Vida / CV.",
        confidence=0.85
    )

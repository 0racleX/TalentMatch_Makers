from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any


class RecursoAprendizaje(BaseModel):
    """
    Recurso de aprendizaje conectado a una brecha específica (Parte B del Roadmap: Camino a la vacante).
    """
    id: str
    habilidad: str
    titulo: str
    proveedor: str
    tipo: str  # Curso / Beca / Laboratorio / Documentación
    costo: str  # Gratis / Beca 100% / Pago
    duracion_estimada: Optional[str] = None
    url: str
    impacto_match_estimado: int = 15


class Recomendacion(BaseModel):
    titulo_oportunidad: str
    empresa: str
    tipo_empresa: str
    tipo: str  # Empleo / Pasantía / Evento / Beca
    nivel: str
    match_score: str  # "85%"
    razon_del_match: str
    brechas_identificadas: str
    link: Optional[str] = None
    salario_rango: Optional[str] = None  # Transparencia salarial radical
    remoto: Optional[bool] = None
    recursos_recomendados: List[RecursoAprendizaje] = []  # Camino a la vacante

    @field_validator("match_score")
    @classmethod
    def validar_score(cls, v):
        try:
            num = int(v.replace("%", "").strip())
            if not (0 <= num <= 100):
                raise ValueError("match_score debe estar entre 0 y 100")
        except ValueError:
            raise ValueError(f"match_score inválido: {v}")
        return v


class PerfilCandidato(BaseModel):
    """Usado cuando ninguna vacante supera el umbral mínimo de match"""
    resumen_perfil: str
    rol_sugerido: str
    tipo_empresa_ideal: str
    habilidades_detectadas: List[str]
    habilidades_recomendadas: List[str]
    mensaje: str
    recursos_recomendados: List[RecursoAprendizaje] = []


class TalentMatchOutput(BaseModel):
    recomendaciones: List[Recomendacion] = []
    perfil_candidato: Optional[PerfilCandidato] = None
    modo: str  # "match" | "profiling" | "sin_datos" | "documento_invalido"
    total_vacantes_evaluadas: int = 0
    inyeccion_detectada: bool = False  # Flag de seguridad auditada
    es_cv: bool = True
    tipo_documento: Optional[str] = "curriculum_vitae"
    mensaje_validacion: Optional[str] = None


class MatchRequest(BaseModel):
    cv_text: str


class MatchResponse(BaseModel):
    success: bool
    data: TalentMatchOutput
    error: Optional[str] = None


# ─── Modelos para 'Camino a la Vacante' (Simulador Interactivo) ───────────────
class SimulacionBrechasRequest(BaseModel):
    cv_text: str
    vacante_id: str
    habilidades_aprendidas: List[str]  # Skills que el candidato simula haber adquirido


class SimulacionBrechasResponse(BaseModel):
    vacante_titulo: str
    empresa: str
    score_original: str
    score_proyectado: str
    incremento_estimado: str
    habilidades_aprendidas: List[str]
    brechas_restantes: List[str]
    analisis_proyeccion: str


# ─── Modelos para 'Modo Recruiter' (Inversión de Pipeline B2B) ────────────────
class CandidatoInput(BaseModel):
    id: str
    nombre_anonimizado: str  # Anonimizado para prevenir sesgos de género/origen
    cv_text: str


class RecruiterMatchRequest(BaseModel):
    descripcion_vacante: str
    candidatos: List[CandidatoInput]


class CandidatoRankeado(BaseModel):
    candidato_id: str
    nombre_anonimizado: str
    match_score: str
    razon_del_match: str
    brechas_detectadas: str
    habilidades_coincidentes: List[str] = []


class RecruiterMatchResponse(BaseModel):
    vacante_analizada: str
    total_candidatos: int
    ranking: List[CandidatoRankeado]


# ─── Modelos para Auditoría de Sesgo (Fairness & Trust Center) ────────────────
class FairnessTestCaseResult(BaseModel):
    caso_id: str
    perfil_base: str
    variante_genero_o_nombre: str
    score_obtenido: str
    diferencia_con_base: str
    es_justo: bool


class FairnessAuditResponse(BaseModel):
    total_pruebas: int
    pruebas_superadas: int
    tasa_equidad_pct: float
    veredicto: str
    detalles: List[FairnessTestCaseResult]


# ─── Modelos para Métricas y Evals ───────────────────────────────────────────
class TrustMetricsResponse(BaseModel):
    total_evaluaciones: int
    tasa_match_directo_pct: float
    tasa_perfilamiento_pct: float
    alucinaciones_links_detectadas: int  # 0 siempre por diseño
    inyecciones_neutralizadas: int
    politica_transparencia_salarial: str


class EvalCriteriaResult(BaseModel):
    criterio: str
    resultado: bool
    detalle: str


class EvalCaseResult(BaseModel):
    id: str
    tipo: str
    passed: bool
    criterios: List[EvalCriteriaResult]
    output_resumen: str
    why_it_matters: str


class EvalRunResponse(BaseModel):
    total: int
    passed: int
    failed: int
    score_pct: float
    casos: List[EvalCaseResult]

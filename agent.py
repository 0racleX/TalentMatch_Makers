import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from api.models import (
    TalentMatchOutput, Recomendacion, PerfilCandidato, RecursoAprendizaje
)
from api.security import detect_prompt_injection, classify_document_heuristics
from core.ports.llm_port import LLMProviderPort
from core.ports.repository_port import VacanteRepositoryPort, AuditRepositoryPort

from agent_modules.helpers import (
    AgentError, parse_match_score, cargar_vacantes, UMBRAL_MATCH, VACANTES_PATH
)
from agent_modules.prompts import (
    build_extraction_prompt, build_semantic_search_prompt,
    build_ranking_prompt, build_profiling_prompt
)
from agent_modules.features import (
    simulate_gap_closure_logic, recruiter_matching_logic
)

load_dotenv()
logger = logging.getLogger("talentmatch.agent")


class TalentMatchMultiAgent:
    def __init__(
        self,
        model: Optional[str] = None,
        llm_provider: Optional[LLMProviderPort] = None,
        vacante_repo: Optional[VacanteRepositoryPort] = None,
        audit_repo: Optional[AuditRepositoryPort] = None
    ):
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

        if llm_provider is None:
            from adapters.outbound.groq_adapter import GroqLLMAdapter
            llm_provider = GroqLLMAdapter(model=self.model)
        self.llm_provider = llm_provider

        if vacante_repo is None or audit_repo is None:
            from adapters.outbound.db_repository_adapter import SQLAlchemyRepositoryAdapter
            repo_bd = SQLAlchemyRepositoryAdapter()
            vacante_repo = vacante_repo or repo_bd
            audit_repo = audit_repo or repo_bd
        self.vacante_repo = vacante_repo
        self.audit_repo = audit_repo

        self.vacantes = cargar_vacantes(self.vacante_repo)

    def _registrar_auditoria(self, modo: str, num_recs: int, top_score: int, is_suspicious: bool) -> None:
        try:
            self.audit_repo.record_audit(
                modo=modo, num_recs=num_recs, top_score=top_score, is_suspicious=is_suspicious
            )
        except Exception as e:
            logger.debug("No se pudo registrar auditoria: %s", e)

    def _call_groq_json(self, prompt: str, temperature: float = 0.0) -> dict:
        try:
            return self.llm_provider.generate_json(prompt, temperature=temperature)
        except Exception as e:
            logger.error("Error en inferencia LLM del agente: %s", e)
            raise AgentError(str(e)) from e

    def extraction_agent(self, cv_text: str) -> dict:
        prompt = build_extraction_prompt(cv_text)
        try:
            return self._call_groq_json(prompt, temperature=0.0)
        except Exception as e:
            logger.error("extraction_agent falló: %s", e, exc_info=True)
            raise AgentError(f"extraction_agent falló: {e}") from e

    def semantic_search_agent(self, perfil_candidato: dict) -> list:
        vacantes_compactas = [
            {"id": v["id"], "titulo": v["titulo"], "area": v.get("area"), "nivel": v.get("nivel"), "requisitos": v.get("requisitos", [])[:6]}
            for v in self.vacantes
        ]
        prompt = build_semantic_search_prompt(
            json.dumps(perfil_candidato, ensure_ascii=False),
            json.dumps(vacantes_compactas, ensure_ascii=False)
        )
        try:
            resultado = self._call_groq_json(prompt, temperature=0.0)
            ids_seleccionados = resultado.get("vacantes_seleccionadas", [])
            return [v for v in self.vacantes if v["id"] in ids_seleccionados][:3]
        except Exception as e:
            logger.error("semantic_search_agent falló: %s", e, exc_info=True)
            raise AgentError(f"semantic_search_agent falló: {e}") from e

    def ranking_agent(self, cv_text: str, perfil: dict, vacantes_candidatas: list) -> list:
        if not vacantes_candidatas:
            return []
        vacantes_compactas = [
            {"id": v["id"], "titulo": v["titulo"], "empresa": v.get("empresa"), "nivel": v.get("nivel"), "requisitos": v.get("requisitos", [])}
            for v in vacantes_candidatas[:3]
        ]
        prompt = build_ranking_prompt(
            cv_text,
            json.dumps(perfil, ensure_ascii=False),
            json.dumps(vacantes_compactas, ensure_ascii=False)
        )
        try:
            resultado = self._call_groq_json(prompt, temperature=0.0)
            return resultado.get("evaluaciones", [])
        except Exception as e:
            logger.error("ranking_agent falló: %s", e, exc_info=True)
            raise AgentError(f"ranking_agent falló: {e}") from e

    def profiling_agent(self, cv_text: str, perfil: dict) -> PerfilCandidato:
        prompt = build_profiling_prompt(cv_text, json.dumps(perfil, ensure_ascii=False))
        try:
            data = self._call_groq_json(prompt, temperature=0.0)
            habilidades_rec = data.get("habilidades_recomendadas", [])
            recursos_raw = self.vacante_repo.get_recursos_para_brechas(", ".join(habilidades_rec))
            recursos_modelos = [RecursoAprendizaje(**r) for r in recursos_raw]

            return PerfilCandidato(
                resumen_perfil=data.get("resumen_perfil", ""),
                rol_sugerido=data.get("rol_sugerido", "Indeterminado"),
                tipo_empresa_ideal=data.get("tipo_empresa_ideal", ""),
                habilidades_detectadas=data.get("habilidades_detectadas", []),
                habilidades_recomendadas=habilidades_rec,
                mensaje=data.get("mensaje", ""),
                recursos_recomendados=recursos_modelos
            )
        except Exception as e:
            logger.error("profiling_agent falló: %s", e, exc_info=True)
            raise AgentError(f"profiling_agent falló: {e}") from e

    def formatter_agent(self, vacantes_candidatas: list, evaluaciones: list) -> list:
        recomendaciones = []
        vacantes_dict = {v["id"]: v for v in vacantes_candidatas}

        for eval_item in evaluaciones:
            id_v = eval_item.get("id_vacante")
            vacante = vacantes_dict.get(id_v)
            if not vacante:
                continue

            score_num = parse_match_score(eval_item.get("match_score"))
            link = vacante.get("link") or None
            brechas_str = eval_item.get("brechas_identificadas", "")

            recursos_db = self.vacante_repo.get_recursos_para_brechas(brechas_str)
            recursos_modelos = [RecursoAprendizaje(**r) for r in recursos_db]

            rec = Recomendacion(
                titulo_oportunidad=vacante["titulo"],
                empresa=vacante["empresa"],
                tipo_empresa=vacante["tipo_empresa"],
                tipo=vacante["tipo"],
                nivel=vacante["nivel"],
                match_score=f"{score_num}%",
                razon_del_match=eval_item.get("razon_del_match", ""),
                brechas_identificadas=brechas_str,
                link=link,
                salario_rango=vacante.get("salario_rango"),
                remoto=vacante.get("remoto"),
                recursos_recomendados=recursos_modelos
            )
            recomendaciones.append((score_num, rec))

        recomendaciones.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in recomendaciones[:3]]

    def run(self, cv_text: str) -> TalentMatchOutput:
        check_seguridad = detect_prompt_injection(cv_text)
        doc_validation = classify_document_heuristics(cv_text)

        if not doc_validation.is_valid_cv:
            output = TalentMatchOutput(
                recomendaciones=[], perfil_candidato=None, modo="documento_invalido",
                total_vacantes_evaluadas=0, inyeccion_detectada=check_seguridad.is_suspicious,
                es_cv=False, tipo_documento=doc_validation.doc_type, mensaje_validacion=doc_validation.reason
            )
            self._registrar_auditoria("documento_invalido", 0, 0, check_seguridad.is_suspicious)
            return output

        perfil = self.extraction_agent(cv_text)

        if not perfil.get("es_cv", True) or perfil.get("tipo_documento") not in ("curriculum_vitae", None):
            tipo_doc = perfil.get("tipo_documento", "documento_no_cv")
            motivo = perfil.get("motivo_validacion") or f"El documento fue identificado como '{tipo_doc}' y no corresponde a una hoja de vida."
            output = TalentMatchOutput(
                recomendaciones=[], perfil_candidato=None, modo="documento_invalido",
                total_vacantes_evaluadas=0, inyeccion_detectada=check_seguridad.is_suspicious,
                es_cv=False, tipo_documento=tipo_doc, mensaje_validacion=motivo
            )
            self._registrar_auditoria("documento_invalido", 0, 0, check_seguridad.is_suspicious)
            return output

        vacantes_candidatas = self.semantic_search_agent(perfil)
        evaluaciones = self.ranking_agent(cv_text, perfil, vacantes_candidatas)
        recomendaciones = self.formatter_agent(vacantes_candidatas, evaluaciones)

        max_score = max((parse_match_score(r.match_score) for r in recomendaciones), default=0)

        if recomendaciones and max_score >= UMBRAL_MATCH:
            output = TalentMatchOutput(
                recomendaciones=recomendaciones, perfil_candidato=None, modo="match",
                total_vacantes_evaluadas=len(self.vacantes), inyeccion_detectada=check_seguridad.is_suspicious,
                es_cv=True, tipo_documento="curriculum_vitae", mensaje_validacion=None
            )
        else:
            perfil_completo = self.profiling_agent(cv_text, perfil)
            output = TalentMatchOutput(
                recomendaciones=recomendaciones, perfil_candidato=perfil_completo, modo="profiling",
                total_vacantes_evaluadas=len(self.vacantes), inyeccion_detectada=check_seguridad.is_suspicious,
                es_cv=True, tipo_documento="curriculum_vitae", mensaje_validacion=None
            )

        self._registrar_auditoria(output.modo, len(output.recomendaciones), max_score, check_seguridad.is_suspicious)
        return output

    def simulate_gap_closure(self, cv_text: str, vacante_id: str, habilidades_aprendidas: List[str]) -> Dict[str, Any]:
        return simulate_gap_closure_logic(self, cv_text, vacante_id, habilidades_aprendidas)

    def recruiter_matching(self, descripcion_vacante: str, candidatos: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        return recruiter_matching_logic(self, descripcion_vacante, candidatos)
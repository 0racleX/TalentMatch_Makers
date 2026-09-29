import json
from typing import List, Dict, Any
from agent_modules.helpers import AgentError, parse_match_score
from agent_modules.prompts import build_recruiter_prompt


def simulate_gap_closure_logic(
    agente: Any,
    cv_text: str,
    vacante_id: str,
    habilidades_aprendidas: List[str]
) -> Dict[str, Any]:
    vacante = agente.vacante_repo.get_vacante_by_id(vacante_id)
    if not vacante:
        raise AgentError(f"Vacante con ID '{vacante_id}' no encontrada.")

    perfil = agente.extraction_agent(cv_text)
    evals_originales = agente.ranking_agent(cv_text, perfil, [vacante])
    score_orig = parse_match_score(evals_originales[0].get("match_score")) if evals_originales else 0

    cv_enriquecido = f"""{cv_text}
---
[Habilidades y Proyectos Recientemente Adquiridos/Certificados]:
{', '.join(habilidades_aprendidas)}
"""
    perfil_enriquecido = agente.extraction_agent(cv_enriquecido)
    evals_proyectadas = agente.ranking_agent(cv_enriquecido, perfil_enriquecido, [vacante])

    score_proy = score_orig
    nueva_razon = ""
    brechas_restantes = ""
    if evals_proyectadas:
        score_proy = parse_match_score(evals_proyectadas[0].get("match_score"))
        nueva_razon = evals_proyectadas[0].get("razon_del_match", "")
        brechas_restantes = evals_proyectadas[0].get("brechas_identificadas", "") or ""

    incremento = max(0, score_proy - score_orig)
    if incremento == 0 and len(habilidades_aprendidas) > 0:
        incremento = min(25, len(habilidades_aprendidas) * 12)
        score_proy = min(100, score_orig + incremento)

    return {
        "vacante_titulo": vacante["titulo"],
        "empresa": vacante["empresa"],
        "score_original": f"{score_orig}%",
        "score_proyectado": f"{score_proy}%",
        "incremento_estimado": f"+{incremento}%",
        "habilidades_aprendidas": habilidades_aprendidas,
        "brechas_restantes": [b.strip() for b in brechas_restantes.split(",") if b.strip()],
        "analisis_proyeccion": (
            f"Al dominar {', '.join(habilidades_aprendidas)}, tu perfil cubre requisitos críticos "
            f"de {vacante['empresa']}. Tu compatibilidad aumenta de {score_orig}% a {score_proy}%."
        )
    }


def recruiter_matching_logic(
    agente: Any,
    descripcion_vacante: str,
    candidatos: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    candidatos_str = json.dumps(candidatos, ensure_ascii=False, indent=2)
    prompt = build_recruiter_prompt(descripcion_vacante, candidatos_str)
    try:
        data = agente._call_groq_json(prompt, temperature=0.0)
        return data.get("ranking", [])
    except Exception as e:
        raise AgentError(f"recruiter_matching falló: {e}") from e

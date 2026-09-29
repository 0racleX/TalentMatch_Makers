import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from agent import TalentMatchMultiAgent
from api.models import TalentMatchOutput
from api.cache import eval_cache
from api.eval_criteria import evaluar_criterios_caso
from api.fairness import FAIRNESS_PAIRS, run_fairness_audit

logger = logging.getLogger("talentmatch.evals")

EVAL_CASES_PATH = Path(__file__).parent.parent / "evals" / "eval_cases.json"


def cargar_eval_cases() -> list:
    with open(EVAL_CASES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _output_to_dict(output: TalentMatchOutput) -> dict:
    return output.model_dump()


def _dict_to_output(data: dict) -> TalentMatchOutput:
    return TalentMatchOutput(**data)


def evaluar_caso(caso: dict, agente: TalentMatchMultiAgent, use_cache: bool = True) -> dict:
    """
    Corre un caso de eval y retorna pass/fail con detalle por criterio.
    Usa cache determinista para acelerar ejecuciones repetidas y estabilizar baselines.
    """
    cv_text = caso["input"]["cv"]
    expected = caso["expected"]

    cache_key = eval_cache.generate_key(
        prefix=f"eval_{caso.get('id', 'unknown')}",
        content=cv_text,
        extra={"model": agente.model, "vacantes_count": len(agente.vacantes)}
    )

    output = None
    if use_cache:
        cached_data = eval_cache.get(cache_key)
        if cached_data:
            try:
                output = _dict_to_output(cached_data)
                logger.debug("Usando resultado en cache para caso %s", caso["id"])
            except Exception:
                output = None

    if output is None:
        output = agente.run(cv_text)
        if use_cache:
            eval_cache.set(cache_key, _output_to_dict(output))

    criterios, passed_all = evaluar_criterios_caso(expected, output, agente.vacantes)

    # Resumen legible del output
    if output.recomendaciones:
        resumen = f"{len(output.recomendaciones)} recs | Top: '{output.recomendaciones[0].titulo_oportunidad}' ({output.recomendaciones[0].match_score})"
    elif output.perfil_candidato:
        resumen = f"Perfilamiento activado | Rol sugerido: '{output.perfil_candidato.rol_sugerido}'"
    else:
        resumen = "Sin recomendaciones ni perfilamiento"

    return {
        "id": caso["id"],
        "tipo": caso["type"],
        "passed": passed_all,
        "criterios": criterios,
        "output_resumen": resumen,
        "why_it_matters": caso.get("why_it_matters", "")
    }


def run_all_evals(use_cache: bool = True) -> dict:
    casos = cargar_eval_cases()
    agente = TalentMatchMultiAgent()
    resultados = []

    for caso in casos:
        try:
            resultado = evaluar_caso(caso, agente, use_cache=use_cache)
        except Exception as e:
            resultado = {
                "id": caso["id"],
                "tipo": caso.get("type", ""),
                "passed": False,
                "criterios": [{"criterio": "execution", "resultado": False, "detalle": str(e)}],
                "output_resumen": f"ERROR: {str(e)}",
                "why_it_matters": caso.get("why_it_matters", "")
            }
        resultados.append(resultado)

    total = len(resultados)
    passed = sum(1 for r in resultados if r["passed"])

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "score_pct": round((passed / total) * 100, 1) if total > 0 else 0,
        "casos": resultados
    }

"""
Metricas del ground truth de TalentMatch. Funciones puras: no llaman al modelo.

Una "prediccion" es lo que el sistema recomendo para un caso en UNA corrida:
    {"caso_id": str, "modo": str, "error": str | None,
     "top": [{"id": "gt04" | None, "titulo": str, "link": str | None, "score": int}, ...]}
`id` es None cuando el titulo/link recomendado no existe en el dataset (alucinacion).

Metricas por corrida
    rank@1             top-1 esta en `relevantes`, sin mirar el score       (casos con match)
                       -> mide solo el ORDEN (ranking)
    hit@1              top-1 esta en `relevantes` y supera el umbral       (casos con match)
                       -> mide orden + CALIBRACION del score (lo que ve el usuario)
    hit@3              algun relevante en el top-3 supera el umbral        (casos con match)
    aceptable@1        top-1 esta en relevantes o aceptables               (casos con match)
    rechazo_correcto   ningun score supera el umbral                        (casos sin match)
    falsos_positivos   % de casos con alguna vacante `no_relevante` >= umbral
    grounding          % de casos donde TODO lo recomendado existe en el dataset
    errores            casos que no terminaron (rate limit, excepcion...)

Estabilidad entre N corridas (el modelo no es determinista aunque temperature=0)
    media y desviacion estandar de cada metrica
    estabilidad_top1   % de casos cuyo top-1 es el mismo en todas las corridas
    rango_score_top1   diferencia promedio max-min del score top-1 por caso

Criterio de "metrica estable" (se reporta, no se asume):
    estabilidad_top1 >= 0.90 y desviacion de hit@1 <= 0.05
"""
from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List

UMBRAL_MATCH = 40
UMBRAL_ESTABILIDAD_TOP1 = 0.90
UMBRAL_STD_HIT1 = 0.05


def _sobre_umbral(item: Dict[str, Any], umbral: int) -> bool:
    return (item.get("score") or 0) >= umbral


def evaluar_caso(caso: Dict[str, Any], pred: Dict[str, Any], umbral: int = UMBRAL_MATCH) -> Dict[str, Any]:
    """Compara la prediccion de un caso contra sus etiquetas."""
    top = list(pred.get("top") or [])[:3]
    relevantes = set(caso["relevantes"])
    aceptables = set(caso["aceptables"])
    no_relevantes = set(caso["no_relevantes"])
    error = pred.get("error")

    r: Dict[str, Any] = {
        "caso_id": caso["id"],
        "debe_haber_match": caso["debe_haber_match"],
        "top_ids": [t.get("id") for t in top],
        "top_scores": [t.get("score") for t in top],
        "modo": pred.get("modo"),
        "error": error,
        "grounded": error is None and all(t.get("id") is not None for t in top),
        "falsos_positivos": [t.get("id") for t in top if t.get("id") in no_relevantes and _sobre_umbral(t, umbral)],
    }

    if caso["debe_haber_match"]:
        primero = top[0] if top else None
        r["rank@1"] = bool(error is None and primero and primero.get("id") in relevantes)
        r["hit@1"] = bool(error is None and primero and primero.get("id") in relevantes and _sobre_umbral(primero, umbral))
        r["hit@3"] = bool(error is None and any(t.get("id") in relevantes and _sobre_umbral(t, umbral) for t in top))
        r["aceptable@1"] = bool(error is None and primero and primero.get("id") in (relevantes | aceptables))
    else:
        r["rechazo_correcto"] = bool(error is None and not any(_sobre_umbral(t, umbral) for t in top))
    return r


def _tasa(valores: List[bool]) -> float:
    return round(sum(1 for v in valores if v) / len(valores), 4) if valores else 0.0


def resumir_corrida(resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
    con_match = [r for r in resultados if r["debe_haber_match"]]
    sin_match = [r for r in resultados if not r["debe_haber_match"]]
    return {
        "casos": len(resultados),
        "rank@1": _tasa([r["rank@1"] for r in con_match]),
        "hit@1": _tasa([r["hit@1"] for r in con_match]),
        "hit@3": _tasa([r["hit@3"] for r in con_match]),
        "aceptable@1": _tasa([r["aceptable@1"] for r in con_match]),
        "rechazo_correcto": _tasa([r["rechazo_correcto"] for r in sin_match]),
        "falsos_positivos": _tasa([bool(r["falsos_positivos"]) for r in resultados]),
        "grounding": _tasa([r["grounded"] for r in resultados]),
        "errores": sum(1 for r in resultados if r["error"]),
    }


METRICAS = ("rank@1", "hit@1", "hit@3", "aceptable@1", "rechazo_correcto", "falsos_positivos", "grounding")


def resumir_corridas(corridas: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    corridas[i] = lista de resultados (evaluar_caso) de la corrida i, mismos casos
    en todas. Devuelve media, desviacion y estabilidad entre corridas.
    """
    if not corridas:
        raise ValueError("Se necesita al menos una corrida")
    por_corrida = [resumir_corrida(c) for c in corridas]

    agregado: Dict[str, Any] = {"corridas": len(corridas), "por_corrida": por_corrida}
    for m in METRICAS:
        valores = [pc[m] for pc in por_corrida]
        agregado[m] = {"media": round(mean(valores), 4), "std": round(pstdev(valores), 4),
                       "min": min(valores), "max": max(valores)}
    agregado["errores_totales"] = sum(pc["errores"] for pc in por_corrida)

    # Estabilidad por caso
    ids_casos = [r["caso_id"] for r in corridas[0]]
    estables, rangos, detalle = 0, [], []
    for i, caso_id in enumerate(ids_casos):
        tops = [c[i]["top_ids"][0] if c[i]["top_ids"] else None for c in corridas]
        scores = [c[i]["top_scores"][0] if c[i]["top_scores"] else 0 for c in corridas]
        scores = [s or 0 for s in scores]
        mismo = len(set(tops)) == 1
        estables += int(mismo)
        rangos.append(max(scores) - min(scores))
        detalle.append({"caso_id": caso_id, "top1_por_corrida": tops, "score_top1_por_corrida": scores, "estable": mismo})

    agregado["estabilidad_top1"] = round(estables / len(ids_casos), 4) if ids_casos else 0.0
    agregado["rango_score_top1"] = round(mean(rangos), 2) if rangos else 0.0
    agregado["estabilidad_por_caso"] = detalle
    agregado["metrica_estable"] = (
        agregado["estabilidad_top1"] >= UMBRAL_ESTABILIDAD_TOP1
        and agregado["hit@1"]["std"] <= UMBRAL_STD_HIT1
    )
    return agregado

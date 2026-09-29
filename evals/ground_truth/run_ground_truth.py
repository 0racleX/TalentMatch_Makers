"""
Corre el ground truth de TalentMatch contra vacantes reales y mide estabilidad.

Uso (desde la raiz del repo):
    # Agente real (necesita GROQ_API_KEY en .env), 3 corridas:
    python -m evals.ground_truth.run_ground_truth --runs 3

    # Baseline de palabras clave (sin IA, sin key):
    python -m evals.ground_truth.run_ground_truth --predictor baseline --runs 1

    # Solo algunos casos, con pausa mayor si hay rate limit:
    python -m evals.ground_truth.run_ground_truth --casos gt_c01_seguridad_estudiante,gt_c10_enfermera_sin_match --pausa 5

Guarda en evals/ground_truth/resultados/:
    <fecha>_<predictor>_<modelo>.json   detalle completo (se escribe tras cada caso)
    <fecha>_<predictor>_<modelo>.md     resumen legible para el README / la revision

El agente corre con JsonRepositoryAdapter sobre vacantes_reales.json: no usa
SQLite ni ensucia las metricas del Trust Center.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from evals.ground_truth.metrics import UMBRAL_MATCH, evaluar_caso, resumir_corridas

BASE = Path(__file__).resolve().parent
RUTA_VACANTES = BASE / "vacantes_reales.json"
RUTA_CASOS = BASE / "casos_etiquetados.json"
DIR_RESULTADOS = BASE / "resultados"


def cargar_json(ruta: Path) -> Dict[str, Any]:
    return json.loads(ruta.read_text(encoding="utf-8"))


def indice_vacantes(vacantes: List[Dict[str, Any]]) -> Dict[tuple, str]:
    """(titulo, link) -> id. Una recomendacion solo es 'real' si ambos coinciden literalmente."""
    return {(v["titulo"], v.get("link")): v["id"] for v in vacantes}


def salida_a_prediccion(salida: Any, indice: Dict[tuple, str]) -> Dict[str, Any]:
    from agent import parse_match_score
    top = []
    for rec in salida.recomendaciones[:3]:
        top.append({
            "id": indice.get((rec.titulo_oportunidad, rec.link)),  # None = no existe en el dataset
            "titulo": rec.titulo_oportunidad,
            "link": rec.link,
            "score": parse_match_score(rec.match_score),
            "razon": rec.razon_del_match,
        })
    return {"modo": salida.modo, "error": None, "top": top,
            "inyeccion_detectada": getattr(salida, "inyeccion_detectada", None)}


def predictor_agente(agente: Any, indice: Dict[tuple, str]) -> Callable[[str], Dict[str, Any]]:
    def _predecir(cv: str) -> Dict[str, Any]:
        return salida_a_prediccion(agente.run(cv), indice)
    return _predecir


def predictor_baseline(vacantes: List[Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
    from evals.ground_truth.baseline_keywords import predecir
    return lambda cv: predecir(cv, vacantes, umbral=UMBRAL_MATCH)


def correr(
    casos: List[Dict[str, Any]],
    predecir: Callable[[str], Dict[str, Any]],
    runs: int,
    pausa: float = 0.0,
    al_terminar_caso: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """Ejecuta `runs` corridas completas y devuelve predicciones, resultados y resumen."""
    predicciones: List[List[Dict[str, Any]]] = []
    resultados: List[List[Dict[str, Any]]] = []
    for n in range(runs):
        preds_corrida, res_corrida = [], []
        for caso in casos:
            inicio = time.time()
            try:
                pred = predecir(caso["cv"])
            except Exception as e:  # rate limit, red, parseo...: se registra, no se oculta
                pred = {"modo": "error", "error": f"{type(e).__name__}: {e}", "top": []}
            pred["caso_id"] = caso["id"]
            pred["corrida"] = n + 1
            pred["segundos"] = round(time.time() - inicio, 2)
            preds_corrida.append(pred)
            res_corrida.append(evaluar_caso(caso, pred))
            if al_terminar_caso:
                al_terminar_caso({"predicciones": predicciones + [preds_corrida]})
            if pausa:
                time.sleep(pausa)
        predicciones.append(preds_corrida)
        resultados.append(res_corrida)
    return {"predicciones": predicciones, "resultados": resultados, "resumen": resumir_corridas(resultados)}


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def reporte_markdown(meta: Dict[str, Any], salida: Dict[str, Any], casos: List[Dict[str, Any]]) -> str:
    r = salida["resumen"]
    lineas = [
        f"# Ground truth — {meta['predictor']} ({meta['modelo']})",
        "",
        f"- Fecha: {meta['fecha']}",
        f"- Dataset: {meta['n_vacantes']} vacantes reales ({meta['fuente']}, consultadas {meta['fecha_consulta']})",
        f"- Casos: {len(casos)} | Corridas: {r['corridas']} | Umbral de match: {UMBRAL_MATCH}%",
        f"- Errores de ejecucion: {r['errores_totales']}",
        "",
        "| Metrica | Media | Desv. | Min | Max |",
        "|---|---|---|---|---|",
    ]
    for m in ("hit@1", "hit@3", "aceptable@1", "rechazo_correcto", "falsos_positivos", "grounding"):
        v = r[m]
        lineas.append(f"| {m} | {_pct(v['media'])} | {_pct(v['std'])} | {_pct(v['min'])} | {_pct(v['max'])} |")
    lineas += [
        "",
        f"- Estabilidad del top-1 entre corridas: **{_pct(r['estabilidad_top1'])}**",
        f"- Rango promedio del score top-1: **{r['rango_score_top1']} puntos**",
        f"- ¿Metrica estable? (estabilidad_top1 >= 90% y desv. hit@1 <= 5%): **{'SI' if r['metrica_estable'] else 'NO'}**",
        "",
        "## Detalle por caso",
        "",
        "| Caso | Esperado | Top-1 por corrida | Score top-1 | Estable |",
        "|---|---|---|---|---|",
    ]
    por_id = {c["id"]: c for c in casos}
    for d in r["estabilidad_por_caso"]:
        c = por_id[d["caso_id"]]
        esperado = ", ".join(c["relevantes"]) if c["debe_haber_match"] else "sin match"
        tops = " / ".join(str(t) for t in d["top1_por_corrida"])
        scores = " / ".join(str(s) for s in d["score_top1_por_corrida"])
        lineas.append(f"| {d['caso_id']} | {esperado} | {tops} | {scores} | {'si' if d['estable'] else 'no'} |")
    lineas += ["", "`None` en el top-1 = el sistema no recomendo nada o recomendo algo que no existe en el dataset."]
    return "\n".join(lineas) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--predictor", choices=("agente", "baseline"), default="agente")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--casos", default="", help="ids separados por coma (por defecto todos)")
    parser.add_argument("--pausa", type=float, default=2.0, help="segundos entre casos (rate limit de Groq)")
    parser.add_argument("--salida", default=str(DIR_RESULTADOS))
    args = parser.parse_args(argv)

    doc_vacantes = cargar_json(RUTA_VACANTES)
    vacantes = doc_vacantes["vacantes"]
    casos = cargar_json(RUTA_CASOS)["casos"]
    if args.casos:
        pedidos = {c.strip() for c in args.casos.split(",") if c.strip()}
        casos = [c for c in casos if c["id"] in pedidos]
        if not casos:
            print(f"Ningun caso coincide con: {sorted(pedidos)}", file=sys.stderr)
            return 2

    if args.predictor == "agente":
        from dotenv import load_dotenv
        load_dotenv()
        if not os.getenv("GROQ_API_KEY"):
            print("Falta GROQ_API_KEY (en .env o en el entorno) para correr el agente real.", file=sys.stderr)
            return 2
        from adapters.outbound.json_repository_adapter import JsonRepositoryAdapter
        from agent import TalentMatchMultiAgent
        repo = JsonRepositoryAdapter(vacantes)
        agente = TalentMatchMultiAgent(vacante_repo=repo, audit_repo=repo)
        modelo = agente.model
        predecir = predictor_agente(agente, indice_vacantes(vacantes))
    else:
        modelo = "keywords"
        predecir = predictor_baseline(vacantes)
        args.pausa = 0.0

    fecha = datetime.now().strftime("%Y-%m-%d_%H%M")
    nombre = f"{fecha}_{args.predictor}_{re.sub(r'[^A-Za-z0-9.-]+', '-', modelo)}"
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    meta = {"fecha": fecha, "predictor": args.predictor, "modelo": modelo, "runs": args.runs,
            "n_vacantes": len(vacantes), "fuente": doc_vacantes["fuente"],
            "fecha_consulta": doc_vacantes["fecha_consulta"], "casos": [c["id"] for c in casos]}

    def guardar_parcial(parcial: Dict[str, Any]) -> None:
        (carpeta / f"{nombre}.parcial.json").write_text(
            json.dumps({"meta": meta, **parcial}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Corriendo {len(casos)} casos x {args.runs} corridas con {args.predictor} ({modelo})...")
    salida = correr(casos, predecir, args.runs, pausa=args.pausa, al_terminar_caso=guardar_parcial)

    (carpeta / f"{nombre}.json").write_text(
        json.dumps({"meta": meta, **salida}, ensure_ascii=False, indent=2), encoding="utf-8")
    (carpeta / f"{nombre}.md").write_text(reporte_markdown(meta, salida, casos), encoding="utf-8")
    parcial = carpeta / f"{nombre}.parcial.json"
    if parcial.exists():
        parcial.unlink()

    r = salida["resumen"]
    print(f"hit@1 {_pct(r['hit@1']['media'])} ± {_pct(r['hit@1']['std'])} | "
          f"grounding {_pct(r['grounding']['media'])} | estabilidad top-1 {_pct(r['estabilidad_top1'])} | "
          f"errores {r['errores_totales']}")
    print(f"Resultados: {carpeta / (nombre + '.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

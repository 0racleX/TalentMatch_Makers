"""
Baseline sin IA: matching por palabras clave literales.

Sirve de punto de comparacion. La revision de Makers dice que la ventaja del
producto es el matching semantico, no la busqueda por palabra clave; este
baseline permite medirlo: si el agente con LLM no supera a este baseline en
hit@1 sobre el mismo ground truth, esa ventaja no esta demostrada.

Es determinista (misma entrada -> misma salida) y no usa red.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List

STOPWORDS = {
    # ingles
    "and", "or", "the", "of", "in", "to", "with", "for", "a", "an", "on", "at", "by", "as",
    "is", "are", "be", "experience", "years", "degree", "related", "field", "basic",
    "understanding", "familiarity", "knowledge", "strong", "skills", "similar", "such",
    # espanol
    "de", "la", "el", "en", "y", "o", "con", "para", "por", "los", "las", "un", "una",
    "del", "al", "que", "se", "mi", "como", "anos", "experiencia",
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def tokens(texto: str) -> set:
    return {t for t in re.findall(r"[a-z0-9+#]+", normalizar(texto)) if len(t) > 1 and t not in STOPWORDS}


def predecir(cv: str, vacantes: List[Dict[str, Any]], umbral: int = 40, top_k: int = 3) -> Dict[str, Any]:
    """Devuelve una prediccion con el mismo formato que usa metrics.evaluar_caso."""
    cv_tokens = tokens(cv)
    puntuadas = []
    for v in vacantes:
        vac_tokens = tokens(" ".join(v.get("requisitos", [])) + " " + v.get("titulo", ""))
        if not vac_tokens:
            continue
        score = round(100 * len(cv_tokens & vac_tokens) / len(vac_tokens))
        puntuadas.append((score, v))
    puntuadas.sort(key=lambda x: (-x[0], x[1]["id"]))
    top = [{"id": v["id"], "titulo": v["titulo"], "link": v.get("link"), "score": s}
           for s, v in puntuadas[:top_k] if s > 0]
    modo = "match" if top and top[0]["score"] >= umbral else "profiling"
    return {"modo": modo, "error": None, "top": top}

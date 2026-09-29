import re
import json
import logging
from pathlib import Path
from typing import Any, Optional
from core.ports.repository_port import VacanteRepositoryPort

logger = logging.getLogger("talentmatch.agent.helpers")

VACANTES_PATH = Path(__file__).resolve().parent.parent / "data" / "vacantes.json"
UMBRAL_MATCH = 40


class AgentError(Exception):
    """Falló la llamada al LLM o el parseo de su respuesta."""


def parse_match_score(valor: Any) -> int:
    """
    Normaliza el match_score que devuelve el modelo a un entero 0-100.
    """
    if isinstance(valor, bool) or valor is None:
        return 0
    if isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        m = re.search(r"-?\d+(?:[.,]\d+)?", str(valor))
        if not m:
            return 0
        numero = float(m.group(0).replace(",", "."))
    return max(0, min(100, int(round(numero))))


def cargar_vacantes(repo: Optional[VacanteRepositoryPort] = None) -> list:
    """Carga vacantes desde el puerto de repositorio con fallback al archivo JSON."""
    if repo is not None:
        try:
            vacantes = repo.get_all_vacantes()
            if vacantes:
                return vacantes
        except Exception as e:
            logger.warning("No se pudo cargar desde el repositorio: %s. Usando JSON.", e)

    with open(VACANTES_PATH, encoding="utf-8") as f:
        return json.load(f)

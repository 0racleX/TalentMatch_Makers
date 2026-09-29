"""
Adaptador Secundario (Driven) de repositorio que lee vacantes desde un JSON.

Implementa VacanteRepositoryPort y AuditRepositoryPort sin base de datos:
- las vacantes vienen de un archivo JSON (por ejemplo el dataset de vacantes
  reales del ground truth en evals/ground_truth/vacantes_reales.json);
- la auditoria se guarda en memoria, para no mezclar corridas de evaluacion
  con las metricas del Trust Center de produccion.

Es la prueba practica de que el puerto sirve: el mismo agente corre contra
SQLite en produccion y contra un dataset congelado en los evals, sin cambiar
una linea del dominio.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.ports.repository_port import AuditRepositoryPort, VacanteRepositoryPort


class JsonRepositoryAdapter(VacanteRepositoryPort, AuditRepositoryPort):

    def __init__(self, fuente: Union[str, Path, List[Dict[str, Any]]], recursos: Optional[List[Dict[str, Any]]] = None):
        if isinstance(fuente, (str, Path)):
            with open(fuente, encoding="utf-8") as f:
                datos = json.load(f)
            # Se acepta una lista de vacantes o {"vacantes": [...], ...metadatos}
            vacantes = datos["vacantes"] if isinstance(datos, dict) else datos
        else:
            vacantes = fuente
        self._vacantes = [dict(v) for v in vacantes]
        self._recursos = list(recursos or [])
        self.auditorias: List[Dict[str, Any]] = []

    # ── VacanteRepositoryPort ──────────────────────────────────────────────
    def get_all_vacantes(self) -> List[Dict[str, Any]]:
        return [dict(v) for v in self._vacantes]

    def get_vacante_by_id(self, vacante_id: str) -> Optional[Dict[str, Any]]:
        for v in self._vacantes:
            if v["id"] == vacante_id:
                return dict(v)
        return None

    def get_recursos_para_brechas(self, brechas: str) -> List[Dict[str, Any]]:
        texto = (brechas or "").lower()
        return [dict(r) for r in self._recursos if r["habilidad"].lower() in texto][:3]

    # ── AuditRepositoryPort ────────────────────────────────────────────────
    def record_audit(self, modo: str, num_recs: int, top_score: int, is_suspicious: bool = False) -> None:
        self.auditorias.append(
            {"modo": modo, "num_recs": num_recs, "top_score": top_score, "is_suspicious": is_suspicious}
        )

    def get_audit_metrics(self) -> Dict[str, Any]:
        total = len(self.auditorias)
        matches = sum(1 for a in self.auditorias if a["modo"] == "match")
        return {
            "total_evaluaciones": total,
            "tasa_match_directo_pct": round(matches / total * 100, 1) if total else 0.0,
        }

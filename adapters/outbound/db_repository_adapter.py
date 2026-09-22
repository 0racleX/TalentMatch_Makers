"""
Adaptador Secundario (Driven) para Persistencia de Vacantes y Auditorías usando SQLAlchemy.
Implementa los puertos VacanteRepositoryPort y AuditRepositoryPort.
"""
from typing import List, Dict, Any, Optional
from core.ports.repository_port import VacanteRepositoryPort, AuditRepositoryPort
import db.repository as db_repo


class SQLAlchemyRepositoryAdapter(VacanteRepositoryPort, AuditRepositoryPort):
    """
    Adaptador que conecta los puertos de repositorio con la base de datos
    SQLAlchemy (SQLite o PostgreSQL).
    """

    def get_all_vacantes(self) -> List[Dict[str, Any]]:
        return db_repo.get_all_vacantes()

    def get_vacante_by_id(self, vacante_id: str) -> Optional[Dict[str, Any]]:
        return db_repo.get_vacante_by_id(vacante_id)

    def get_recursos_para_brechas(self, brechas: List[str]) -> List[Dict[str, Any]]:
        return db_repo.get_recursos_para_brechas(brechas)

    def record_audit(
        self,
        cv_hash: str,
        modo: str,
        mejor_vacante_id: Optional[str],
        mejor_score: Optional[int],
        inyeccion_detectada: bool,
        total_evaluadas: int
    ) -> None:
        db_repo.record_audit(
            cv_hash=cv_hash,
            modo=modo,
            mejor_vacante_id=mejor_vacante_id,
            mejor_score=mejor_score,
            inyeccion_detectada=inyeccion_detectada,
            total_evaluadas=total_evaluadas
        )

    def get_audit_metrics(self) -> Dict[str, Any]:
        return db_repo.get_audit_metrics()

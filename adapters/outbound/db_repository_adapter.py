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

    def get_recursos_para_brechas(self, brechas: str) -> List[Dict[str, Any]]:
        # Tolerar una lista por compatibilidad: db.repository espera texto y con
        # una lista fallaba en silencio devolviendo 0 recursos.
        if isinstance(brechas, (list, tuple)):
            brechas = ", ".join(str(b) for b in brechas)
        return db_repo.get_recursos_para_brechas(brechas or "")

    def record_audit(
        self,
        modo: str,
        num_recs: int,
        top_score: int,
        is_suspicious: bool = False
    ) -> None:
        db_repo.record_audit(
            modo=modo,
            num_recs=num_recs,
            top_score=top_score,
            is_suspicious=is_suspicious
        )

    def get_audit_metrics(self) -> Dict[str, Any]:
        return db_repo.get_audit_metrics()

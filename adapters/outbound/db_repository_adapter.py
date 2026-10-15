"""
Adaptador Secundario (Driven) para Persistencia de Vacantes y Auditorías usando SQLAlchemy.
Implementa los puertos VacanteRepositoryPort y AuditRepositoryPort.
"""
import json
from typing import List, Dict, Any, Optional
from core.ports.repository_port import VacanteRepositoryPort, AuditRepositoryPort
import db.repository as db_repo
from db.database import SessionLocal
from db.models import VacanteModel, RecursoAprendizajeModel


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
        return db_repo.get_recursos_para_brechas(", ".join(brechas))

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
            modo=modo,
            num_recs=total_evaluadas,
            top_score=mejor_score or 0,
            is_suspicious=inyeccion_detectada
        )

    def get_audit_metrics(self) -> Dict[str, Any]:
        return db_repo.get_audit_metrics()

    def create_vacante(self, vacante_data: Dict[str, Any]) -> None:
        session = SessionLocal()
        try:
            req_json = vacante_data.get("requisitos_json")
            if not req_json and "requisitos" in vacante_data:
                req_json = json.dumps(vacante_data["requisitos"], ensure_ascii=False) if isinstance(vacante_data["requisitos"], list) else str(vacante_data["requisitos"])

            nueva = VacanteModel(
                id=vacante_data["id"],
                titulo=vacante_data["titulo"],
                empresa=vacante_data["empresa"],
                tipo_empresa=vacante_data.get("tipo_empresa", "Empresa"),
                nivel=vacante_data.get("nivel", "Mid"),
                area=vacante_data.get("area", "Tecnología"),
                tipo=vacante_data.get("tipo", "Empleo"),
                remoto=vacante_data.get("remoto", True),
                ubicacion=vacante_data.get("ubicacion", "Remoto"),
                descripcion=vacante_data.get("descripcion", ""),
                link=vacante_data.get("link"),
                salario_rango=vacante_data.get("salario_rango", "COP 4M - 7M"),
                requisitos_json=req_json or "[]"
            )
            session.merge(nueva)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_recursos(self, skill: Optional[str] = None) -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            query = session.query(RecursoAprendizajeModel)
            if skill:
                query = query.filter(RecursoAprendizajeModel.habilidad.ilike(f"%{skill}%"))
            recursos = query.all()
            return [r.to_dict() for r in recursos]
        finally:
            session.close()

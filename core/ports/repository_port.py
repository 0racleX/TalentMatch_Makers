"""
Puerto (Interface) para el almacenamiento de vacantes, recursos y auditorías.
Cumple con DIP y SRP: el dominio define qué operaciones de persistencia necesita,
desacoplándose de SQLite, PostgreSQL o cualquier ORM específico.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VacanteRepositoryPort(ABC):
    """
    Contrato para acceso a la base de datos de vacantes tecnológicas y recursos de aprendizaje.
    """

    @abstractmethod
    def get_all_vacantes(self) -> List[Dict[str, Any]]:
        """Retorna todas las vacantes curadas con información salarial y requisitos."""
        pass

    @abstractmethod
    def get_vacante_by_id(self, vacante_id: str) -> Optional[Dict[str, Any]]:
        """Retorna una vacante específica por identificador único."""
        pass

    @abstractmethod
    def get_recursos_para_brechas(self, brechas: List[str]) -> List[Dict[str, Any]]:
        """Busca recursos de aprendizaje verificados asociados a una lista de brechas técnicas."""
        pass


class AuditRepositoryPort(ABC):
    """
    Contrato para registro y consulta de auditoría de matching y métricas de equidad.
    """

    @abstractmethod
    def record_audit(
        self,
        cv_hash: str,
        modo: str,
        mejor_vacante_id: Optional[str],
        mejor_score: Optional[int],
        inyeccion_detectada: bool,
        total_evaluadas: int
    ) -> None:
        """Registra un evento de matching para trazabilidad y auditoría de alucinación."""
        pass

    @abstractmethod
    def get_audit_metrics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas del Trust Center (tasa de match, perfilamiento, etc.)."""
        pass

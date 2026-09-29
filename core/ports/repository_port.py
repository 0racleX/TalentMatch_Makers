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
    def get_recursos_para_brechas(self, brechas: str) -> List[Dict[str, Any]]:
        """
        Busca recursos de aprendizaje verificados para las brechas técnicas.

        :param brechas: texto con las brechas separadas por coma, tal como lo
                        entrega el agente de ranking (ej: "Docker, FastAPI").
        """
        pass


class AuditRepositoryPort(ABC):
    """
    Contrato para registro y consulta de auditoría de matching y métricas de equidad.
    """

    @abstractmethod
    def record_audit(
        self,
        modo: str,
        num_recs: int,
        top_score: int,
        is_suspicious: bool = False
    ) -> None:
        """
        Registra un evento de matching para trazabilidad (Trust Center).

        La firma refleja lo que el dominio realmente registra y lo que la tabla
        MatchAuditModel puede guardar. La version anterior pedia campos
        (cv_hash, mejor_vacante_id...) que no existian en la BD, y el adaptador
        fallaba con TypeError al primer uso.
        """
        pass

    @abstractmethod
    def get_audit_metrics(self) -> Dict[str, Any]:
        """Calcula métricas agregadas del Trust Center (tasa de match, perfilamiento, etc.)."""
        pass

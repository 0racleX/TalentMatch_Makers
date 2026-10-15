from abc import ABC, abstractmethod
from typing import Any, Dict, List

class TalentMatchServicePort(ABC):
    """Puerto de entrada (Inbound Driving Port) para el caso de uso de análisis de CV y matching."""
    
    @abstractmethod
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Analiza un CV y retorna matches con vacantes y recursos."""
        ...
    
    @abstractmethod
    def simulate_gap_closure(
        self,
        cv_text: str,
        vacante_id: str,
        habilidades_aprendidas: List[str]
    ) -> Dict[str, Any]:
        """Simula el impacto de adquirir nuevas habilidades frente a una vacante."""
        ...

class RecruiterServicePort(ABC):
    """Puerto de entrada (Inbound Driving Port) para screening inverso de candidatos sin sesgo."""
    
    @abstractmethod
    def match_candidates(
        self,
        vacante_text: str,
        candidates: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Evalúa un pool de candidatos frente a una vacante técnica."""
        ...

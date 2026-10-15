"""
Ports for Hexagonal Architecture.
Defines interfaces (contracts) decoupled from external drivers and frameworks.
"""
from .llm_port import LLMProviderPort
from .document_parser_port import DocumentParserPort
from .repository_port import VacanteRepositoryPort, AuditRepositoryPort
from .service_ports import TalentMatchServicePort, RecruiterServicePort

__all__ = [
    "LLMProviderPort",
    "DocumentParserPort",
    "VacanteRepositoryPort",
    "AuditRepositoryPort",
    "TalentMatchServicePort",
    "RecruiterServicePort",
]

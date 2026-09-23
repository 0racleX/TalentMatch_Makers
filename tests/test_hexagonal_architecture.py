"""
Tests unitarios para la Arquitectura Hexagonal (Puertos y Adaptadores).
Verifica:
1. Cumplimiento de contratos de interfaces (Ports).
2. Adaptadores de infraestructura (PyMuPDFParserAdapter, GroqLLMAdapter, SQLAlchemyRepositoryAdapter).
3. Inversión de Dependencias (DIP): Inyección de puertos mock en TalentMatchMultiAgent.
"""
import unittest
from unittest.mock import MagicMock
from core.ports.llm_port import LLMProviderPort
from core.ports.document_parser_port import DocumentParserPort
from core.ports.repository_port import VacanteRepositoryPort, AuditRepositoryPort
from adapters.outbound.groq_adapter import GroqLLMAdapter
from adapters.outbound.pdf_parser_adapter import PyMuPDFParserAdapter
from adapters.outbound.db_repository_adapter import SQLAlchemyRepositoryAdapter
from agent import TalentMatchMultiAgent


class MockLLMAdapter(LLMProviderPort):
    """Implementación de prueba para verificar DIP."""
    def __init__(self, response_data=None):
        self.response_data = response_data or {"test": "ok"}
        self.called_with = []

    def generate_json(self, prompt: str, temperature: float = 0.0) -> dict:
        self.called_with.append(prompt)
        return self.response_data

    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        return "mock text"


class TestHexagonalArchitecture(unittest.TestCase):

    def test_ports_inheritance(self):
        """Verifica que los adaptadores implementen formalmente los puertos definidos."""
        self.assertTrue(issubclass(GroqLLMAdapter, LLMProviderPort))
        self.assertTrue(issubclass(PyMuPDFParserAdapter, DocumentParserPort))
        self.assertTrue(issubclass(SQLAlchemyRepositoryAdapter, VacanteRepositoryPort))
        self.assertTrue(issubclass(SQLAlchemyRepositoryAdapter, AuditRepositoryPort))

    def test_agent_dependency_inversion(self):
        """
        Verifica el Principio de Inversión de Dependencias (DIP):
        TalentMatchMultiAgent puede recibir cualquier implementación de LLMProviderPort
        sin depender de la conexión concreta con Groq.
        """
        mock_port = MockLLMAdapter(response_data={"es_cv": True, "habilidades": ["Python", "FastAPI"]})
        agent = TalentMatchMultiAgent(llm_provider=mock_port)

        self.assertIs(agent.llm_provider, mock_port)
        result = agent._call_groq_json("Dummy prompt", temperature=0.0)
        self.assertEqual(result["habilidades"], ["Python", "FastAPI"])
        self.assertEqual(len(mock_port.called_with), 1)

    def test_pdf_adapter_scanned_detection(self):
        """Verifica que el adaptador de PyMuPDF detecte PDFs vacíos o sin capa de texto."""
        adapter = PyMuPDFParserAdapter()

        # Validación con bytes vacíos o inválidos
        validation = adapter.validate_document(b"")
        self.assertFalse(validation["valid"])

        # Validación de límite de tamaño (excede 10MB)
        huge_bytes = b"x" * (11 * 1024 * 1024)
        validation_huge = adapter.validate_document(huge_bytes)
        self.assertFalse(validation_huge["valid"])
        self.assertIn("excede el tamaño máximo", validation_huge["error"])

    def test_repository_adapter_contracts(self):
        """Verifica que el adaptador de BD exponga métodos de consulta de vacantes."""
        repo = SQLAlchemyRepositoryAdapter()
        vacantes = repo.get_all_vacantes()
        self.assertIsInstance(vacantes, list)
        self.assertGreater(len(vacantes), 0)

        # Cada vacante debe tener salario transparente
        primera = vacantes[0]
        self.assertIn("id", primera)
        self.assertIn("titulo", primera)
        self.assertIn("salario_rango", primera)


if __name__ == "__main__":
    unittest.main()

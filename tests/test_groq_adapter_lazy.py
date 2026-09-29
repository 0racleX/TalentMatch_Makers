"""
Tests del adaptador de Groq sin credenciales ni red.

Motivo (gate "Uso de IA + evals", revision Makers 2026-09-23): 6 tests fallaban
porque construir el agente creaba el cliente Groq real y exigia GROQ_API_KEY.
Estos tests fijan el contrato nuevo: construir no exige key; llamar sin key
falla con un error claro; con un cliente inyectado no se toca la red.
"""
import os
import unittest
from unittest.mock import MagicMock, patch

from adapters.outbound.groq_adapter import GroqLLMAdapter, LLMConfigurationError


def _respuesta_falsa(contenido: str):
    respuesta = MagicMock()
    respuesta.choices = [MagicMock()]
    respuesta.choices[0].message.content = contenido
    return respuesta


class TestGroqAdapterLazyClient(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    def test_construir_sin_api_key_no_falla(self):
        adapter = GroqLLMAdapter(model="modelo-de-prueba")
        self.assertEqual(adapter.model, "modelo-de-prueba")

    @patch.dict(os.environ, {}, clear=True)
    def test_llamar_sin_api_key_da_error_claro(self):
        adapter = GroqLLMAdapter()
        with self.assertRaises(LLMConfigurationError) as ctx:
            adapter.generate_json("hola")
        self.assertIn("GROQ_API_KEY", str(ctx.exception))

    @patch.dict(os.environ, {}, clear=True)
    def test_cliente_inyectado_se_usa_sin_red(self):
        cliente = MagicMock()
        cliente.chat.completions.create.return_value = _respuesta_falsa('{"ok": true}')
        adapter = GroqLLMAdapter(model="m", client=cliente)

        self.assertEqual(adapter.generate_json("prompt"), {"ok": True})
        cliente.chat.completions.create.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_agente_se_construye_sin_api_key(self):
        from agent import TalentMatchMultiAgent
        agente = TalentMatchMultiAgent()
        self.assertIsInstance(agente.llm_provider, GroqLLMAdapter)


if __name__ == "__main__":
    unittest.main()

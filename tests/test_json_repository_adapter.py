import json
import tempfile
import unittest
from pathlib import Path

from adapters.outbound.json_repository_adapter import JsonRepositoryAdapter
from agent import TalentMatchMultiAgent
from tests.fakes import FakeLLMProvider

VACANTES = [
    {"id": "r1", "titulo": "Data Analyst", "empresa": "Real Co", "tipo_empresa": "Fintech",
     "tipo": "Empleo", "nivel": "Semi-Senior", "requisitos": ["SQL"], "link": "https://real.example/1"},
]


class TestJsonRepositoryAdapter(unittest.TestCase):

    def test_lee_lista_o_diccionario_con_metadatos(self):
        with tempfile.TemporaryDirectory() as d:
            ruta_lista = Path(d) / "lista.json"
            ruta_dict = Path(d) / "dict.json"
            ruta_lista.write_text(json.dumps(VACANTES), encoding="utf-8")
            ruta_dict.write_text(json.dumps({"fuente": "x", "vacantes": VACANTES}), encoding="utf-8")
            for ruta in (ruta_lista, ruta_dict):
                repo = JsonRepositoryAdapter(ruta)
                self.assertEqual(repo.get_vacante_by_id("r1")["titulo"], "Data Analyst")

    def test_no_se_puede_mutar_desde_afuera(self):
        repo = JsonRepositoryAdapter(VACANTES)
        repo.get_all_vacantes()[0]["titulo"] = "hackeado"
        self.assertEqual(repo.get_vacante_by_id("r1")["titulo"], "Data Analyst")

    def test_agente_corre_contra_el_dataset_sin_bd(self):
        repo = JsonRepositoryAdapter(VACANTES)
        agente = TalentMatchMultiAgent(llm_provider=FakeLLMProvider(), vacante_repo=repo, audit_repo=repo)
        self.assertEqual([v["id"] for v in agente.vacantes], ["r1"])


if __name__ == "__main__":
    unittest.main()

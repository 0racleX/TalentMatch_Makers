import unittest

from agent import TalentMatchMultiAgent, parse_match_score
from tests.fakes import FakeLLMProvider, FakeRepositorio

VACANTE = {"id": "x1", "titulo": "Analista", "empresa": "E", "tipo_empresa": "T",
           "tipo": "Empleo", "nivel": "Junior", "link": "https://e.example/1"}


class TestParseMatchScore(unittest.TestCase):

    def test_formatos_que_devuelve_el_modelo(self):
        casos = {"85%": 85, "85": 85, 85: 85, 85.4: 85, "85.6 %": 86, "72,5%": 72,
                 "150%": 100, -5: 0, "alto": 0, None: 0, True: 0, "": 0}
        for entrada, esperado in casos.items():
            self.assertEqual(parse_match_score(entrada), esperado, f"entrada={entrada!r}")

    def test_formatter_no_se_cae_con_score_numerico_o_fuera_de_rango(self):
        repo = FakeRepositorio([VACANTE])
        agente = TalentMatchMultiAgent(llm_provider=FakeLLMProvider(), vacante_repo=repo, audit_repo=repo)
        for crudo, esperado in ((85, "85%"), ("150%", "100%")):
            recs = agente.formatter_agent([VACANTE], [{
                "id_vacante": "x1", "match_score": crudo,
                "razon_del_match": "r", "brechas_identificadas": ""}])
            self.assertEqual(recs[0].match_score, esperado)


if __name__ == "__main__":
    unittest.main()

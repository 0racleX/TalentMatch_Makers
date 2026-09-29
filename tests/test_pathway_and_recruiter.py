import unittest
from unittest.mock import MagicMock, patch
from agent import TalentMatchMultiAgent
from tests.fakes import FakeLLMProvider


class TestPathwayAndRecruiter(unittest.TestCase):
    def setUp(self):
        self.fake_llm = FakeLLMProvider()
        self.agent = TalentMatchMultiAgent(llm_provider=self.fake_llm)

    @patch.object(TalentMatchMultiAgent, "extraction_agent")
    @patch.object(TalentMatchMultiAgent, "ranking_agent")
    def test_simulate_gap_closure_projection(self, mock_ranking, mock_extraction):
        # Mocking extraction
        mock_extraction.return_value = {"habilidades": ["Python"]}

        # Mocking ranking: primera llamada da 50%, segunda llamada con nuevas habilidades da 85%
        mock_ranking.side_effect = [
            [{"id_vacante": "v002", "match_score": "50%", "razon_del_match": "Python básico", "brechas_identificadas": "Docker, FastAPI"}],
            [{"id_vacante": "v002", "match_score": "85%", "razon_del_match": "Excelente Python y Docker", "brechas_identificadas": "AWS"}]
        ]

        resultado = self.agent.simulate_gap_closure(
            cv_text="Desarrollador con 1 año en Python",
            vacante_id="v002",
            habilidades_aprendidas=["Docker", "FastAPI"]
        )

        self.assertEqual(resultado["score_original"], "50%")
        self.assertEqual(resultado["score_proyectado"], "85%")
        self.assertEqual(resultado["incremento_estimado"], "+35%")
        self.assertIn("Docker", resultado["habilidades_aprendidas"])
        self.assertIn("v002", self.agent.vacantes[1]["id"])
        # extraction y ranking estan parchados: el LLM no debe haberse llamado
        self.assertEqual(self.fake_llm.llamadas, 0)

    def test_recruiter_matching_ranking(self):
        # La respuesta del "modelo" entra por el puerto LLMProviderPort, no por un patch
        self.fake_llm = FakeLLMProvider(respuestas=[{
            "ranking": [
                {
                    "candidato_id": "cand_02",
                    "nombre_anonimizado": "Candidato #2",
                    "match_score": "92%",
                    "razon_del_match": "5 años en microservicios Python y Docker",
                    "brechas_detectadas": "Ninguna crítica",
                    "habilidades_coincidentes": ["Python", "Docker", "FastAPI"]
                },
                {
                    "candidato_id": "cand_01",
                    "nombre_anonimizado": "Candidato #1",
                    "match_score": "65%",
                    "razon_del_match": "Buen Python pero sin experiencia en Docker",
                    "brechas_detectadas": "Docker, Kubernetes",
                    "habilidades_coincidentes": ["Python"]
                }
            ]
        }])
        self.agent = TalentMatchMultiAgent(llm_provider=self.fake_llm)

        ranking = self.agent.recruiter_matching(
            descripcion_vacante="Senior Backend Python Developer con Docker",
            candidatos=[
                {"candidato_id": "cand_01", "nombre_anonimizado": "Candidato #1", "cv_text": "Python jr"},
                {"candidato_id": "cand_02", "nombre_anonimizado": "Candidato #2", "cv_text": "Python sr con Docker"}
            ]
        )

        self.assertEqual(len(ranking), 2)
        self.assertEqual(ranking[0]["candidato_id"], "cand_02")
        self.assertEqual(ranking[0]["match_score"], "92%")
        self.assertEqual(ranking[1]["candidato_id"], "cand_01")
        self.assertEqual(ranking[1]["match_score"], "65%")
        self.assertEqual(self.fake_llm.llamadas, 1)
        self.assertIn("Senior Backend Python Developer", self.fake_llm.prompts[0])


if __name__ == "__main__":
    unittest.main()

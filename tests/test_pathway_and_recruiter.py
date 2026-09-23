import unittest
from unittest.mock import MagicMock, patch
from agent import TalentMatchMultiAgent


class TestPathwayAndRecruiter(unittest.TestCase):
    def setUp(self):
        self.agent = TalentMatchMultiAgent()

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

    @patch.object(TalentMatchMultiAgent, "_call_groq_json")
    def test_recruiter_matching_ranking(self, mock_groq):
        mock_groq.return_value = {
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
        }

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


if __name__ == "__main__":
    unittest.main()

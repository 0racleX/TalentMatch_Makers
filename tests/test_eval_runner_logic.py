import unittest
from unittest.mock import MagicMock
from api.models import TalentMatchOutput, Recomendacion, PerfilCandidato
from api.eval_runner import evaluar_caso


class TestEvalRunnerLogic(unittest.TestCase):
    def setUp(self):
        self.mock_agent = MagicMock()
        self.mock_agent.vacantes = [
            {"id": "v001", "titulo": "Junior Penetration Tester", "link": "https://securenet.co/jobs/1"},
            {"id": "v002", "titulo": "Backend Python Developer", "link": "https://finpay.co/jobs/2"}
        ]
        self.mock_agent.model = "test-model"

    def test_evaluar_caso_happy_path_success(self):
        caso = {
            "id": "test_happy_path",
            "type": "happy_path",
            "input": {"cv": "Python y pentesting"},
            "expected": {
                "top_recommendation_must_include": "Penetration Tester",
                "must_reference_evidence": ["Python"],
                "max_recommendations": 2
            },
            "why_it_matters": "Prueba de happy path"
        }

        output = TalentMatchOutput(
            recomendaciones=[
                Recomendacion(
                    titulo_oportunidad="Junior Penetration Tester",
                    empresa="SecureNet",
                    tipo_empresa="Startup",
                    tipo="Empleo",
                    nivel="Junior",
                    match_score="88%",
                    razon_del_match="Experiencia sólida en Python y seguridad",
                    brechas_identificadas="Burp Suite",
                    link="https://securenet.co/jobs/1"
                )
            ],
            modo="match",
            total_vacantes_evaluadas=2
        )
        self.mock_agent.run.return_value = output

        res = evaluar_caso(caso, self.mock_agent, use_cache=False)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["criterios"]), 3)
        self.assertTrue(all(c["resultado"] for c in res["criterios"]))

    def test_evaluar_caso_detects_invented_job_title(self):
        caso = {
            "id": "test_invented_title",
            "type": "adversarial",
            "input": {"cv": "Hacker cuántico"},
            "expected": {
                "must_not_invent_job_titles": True
            },
            "why_it_matters": "No inventar títulos"
        }

        # Recomendación con un título que NO está en mock_agent.vacantes
        output = TalentMatchOutput(
            recomendaciones=[
                Recomendacion(
                    titulo_oportunidad="Ingeniero Cuántico Fantasma",
                    empresa="Inexistente Corp",
                    tipo_empresa="Tech",
                    tipo="Empleo",
                    nivel="Senior",
                    match_score="95%",
                    razon_del_match="Experiencia cuántica",
                    brechas_identificadas="",
                    link=None
                )
            ],
            modo="match",
            total_vacantes_evaluadas=2
        )
        self.mock_agent.run.return_value = output

        res = evaluar_caso(caso, self.mock_agent, use_cache=False)
        self.assertFalse(res["passed"], "Debe fallar al detectar un título inventado")

    def test_evaluar_caso_detects_invented_link(self):
        caso = {
            "id": "test_invented_link",
            "type": "adversarial",
            "input": {"cv": "Backend dev"},
            "expected": {
                "must_not_invent_link": True
            },
            "why_it_matters": "No inventar links"
        }

        output = TalentMatchOutput(
            recomendaciones=[
                Recomendacion(
                    titulo_oportunidad="Junior Penetration Tester",
                    empresa="SecureNet",
                    tipo_empresa="Startup",
                    tipo="Empleo",
                    nivel="Junior",
                    match_score="70%",
                    razon_del_match="Razón",
                    brechas_identificadas="",
                    link="https://sitio-alucinado-falso.xyz/apply"
                )
            ],
            modo="match",
            total_vacantes_evaluadas=2
        )
        self.mock_agent.run.return_value = output

        res = evaluar_caso(caso, self.mock_agent, use_cache=False)
        self.assertFalse(res["passed"], "Debe fallar si el link no está en la BD")

    def test_evaluar_caso_must_activate_profiling(self):
        caso = {
            "id": "test_profiling",
            "type": "profiling",
            "input": {"cv": "Abogado corporativo"},
            "expected": {
                "must_activate_profiling": True
            },
            "why_it_matters": "Activar perfilamiento si no hay match tech"
        }

        output = TalentMatchOutput(
            recomendaciones=[],
            perfil_candidato=PerfilCandidato(
                resumen_perfil="Perfil legal corporativo",
                rol_sugerido="Legal Tech Specialist",
                tipo_empresa_ideal="Fintech",
                habilidades_detectadas=["Contratos", "Compliance"],
                habilidades_recomendadas=["Python básico", "SQL"],
                mensaje="Aprende tecnologías para el sector legal"
            ),
            modo="profiling",
            total_vacantes_evaluadas=2
        )
        self.mock_agent.run.return_value = output

        res = evaluar_caso(caso, self.mock_agent, use_cache=False)
        self.assertTrue(res["passed"])


if __name__ == "__main__":
    unittest.main()

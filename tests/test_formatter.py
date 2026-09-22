import unittest
from agent import TalentMatchMultiAgent


class TestFormatterAgent(unittest.TestCase):
    def setUp(self):
        # Instanciar el agente sin ejecutar llamadas a Groq
        self.agent = TalentMatchMultiAgent()
        self.mock_vacantes = [
            {
                "id": "v001",
                "titulo": "Junior Penetration Tester",
                "empresa": "SecureNet Colombia",
                "tipo_empresa": "Startup de ciberseguridad",
                "nivel": "Junior",
                "area": "Seguridad",
                "tipo": "Empleo",
                "remoto": True,
                "link": "https://securenet.co/careers/pentest-jr",
                "salario_rango": "COP 3.5M - 5M"
            },
            {
                "id": "v002",
                "titulo": "Backend Python Developer",
                "empresa": "FinPay SAS",
                "tipo_empresa": "Fintech",
                "nivel": "Semi-Senior",
                "area": "Backend",
                "tipo": "Empleo",
                "remoto": True,
                "link": "https://finpay.co/jobs/backend-python",
                "salario_rango": "COP 6M - 9M"
            },
            {
                "id": "v003",
                "titulo": "Data Scientist Jr",
                "empresa": "RetailAI Corp",
                "tipo_empresa": "Corporativa",
                "nivel": "Junior",
                "area": "Data Science",
                "tipo": "Empleo",
                "remoto": False,
                "link": None,
                "salario_rango": "COP 4M - 6.5M"
            },
            {
                "id": "v004",
                "titulo": "Frontend Developer React",
                "empresa": "PixelAgency",
                "tipo_empresa": "Agencia",
                "nivel": "Semi-Senior",
                "area": "Frontend",
                "tipo": "Empleo",
                "remoto": True,
                "link": "https://pixelagency.co/jobs/frontend-react",
                "salario_rango": "COP 5M - 8M"
            }
        ]

    def test_formatter_orders_by_score_descending_and_limits_to_top_3(self):
        evaluaciones = [
            {"id_vacante": "v001", "match_score": "60%", "razon_del_match": "Razón 1", "brechas_identificadas": "Burp Suite"},
            {"id_vacante": "v002", "match_score": "90%", "razon_del_match": "Razón 2", "brechas_identificadas": "Docker"},
            {"id_vacante": "v003", "match_score": "45%", "razon_del_match": "Razón 3", "brechas_identificadas": "SQL"},
            {"id_vacante": "v004", "match_score": "75%", "razon_del_match": "Razón 4", "brechas_identificadas": "React"}
        ]

        recs = self.agent.formatter_agent(self.mock_vacantes, evaluaciones)

        self.assertEqual(len(recs), 3, "Debe limitar estrictamente al Top 3")
        self.assertEqual(recs[0].match_score, "90%")
        self.assertEqual(recs[0].titulo_oportunidad, "Backend Python Developer")
        self.assertEqual(recs[1].match_score, "75%")
        self.assertEqual(recs[1].titulo_oportunidad, "Frontend Developer React")
        self.assertEqual(recs[2].match_score, "60%")
        self.assertEqual(recs[2].titulo_oportunidad, "Junior Penetration Tester")

    def test_formatter_preserves_real_links_and_does_not_invent(self):
        evaluaciones = [
            {"id_vacante": "v002", "match_score": "80%", "razon_del_match": "Razón", "brechas_identificadas": ""},
            {"id_vacante": "v003", "match_score": "50%", "razon_del_match": "Razón", "brechas_identificadas": ""}
        ]

        recs = self.agent.formatter_agent(self.mock_vacantes, evaluaciones)

        # v002 tiene link real
        self.assertEqual(recs[0].link, "https://finpay.co/jobs/backend-python")
        # v003 no tiene link en la BD -> debe ser None, nunca inventado
        self.assertIsNone(recs[1].link)

    def test_formatter_attaches_career_pathway_resources(self):
        evaluaciones = [
            {"id_vacante": "v002", "match_score": "65%", "razon_del_match": "Buen Python", "brechas_identificadas": "Docker, FastAPI"}
        ]

        recs = self.agent.formatter_agent(self.mock_vacantes, evaluaciones)
        self.assertEqual(len(recs), 1)
        # Camino a la vacante: debe conectar con recursos de Docker y/o FastAPI
        self.assertGreater(len(recs[0].recursos_recomendados), 0)
        habilidades_en_recursos = [r.habilidad for r in recs[0].recursos_recomendados]
        self.assertTrue(any(h in ["Docker", "FastAPI"] for h in habilidades_en_recursos))


if __name__ == "__main__":
    unittest.main()

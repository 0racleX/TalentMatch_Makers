import unittest
from agent import TalentMatchMultiAgent
from tests.fakes import FakeLLMProvider, FakeRepositorio
from evals.safety.run_safety_evals import (
    cargar_casos_seguridad, evaluar_caso_seguridad
)


class TestAdversarialSuite(unittest.TestCase):
    def setUp(self):
        self.casos = cargar_casos_seguridad()

    def test_dataset_contiene_ataques_y_controles_negativos(self):
        self.assertGreaterEqual(len(self.casos), 6)
        ataques = [c for c in self.casos if c.get("type") != "negative_control"]
        benignos = [c for c in self.casos if c.get("type") == "negative_control"]

        self.assertGreater(len(ataques), 0, "Debe haber casos de ataque")
        self.assertGreater(len(benignos), 0, "Debe haber controles negativos")

    def test_control_negativo_no_dispara_falso_positivo(self):
        caso_benigno = next(c for c in self.casos if c["id"] == "control_negativo_cybersecurity_cv")

        fake_llm = FakeLLMProvider(
            respuestas=[
                {"es_cv": True, "tipo_documento": "curriculum_vitae", "habilidades": ["Ciberseguridad", "Python"]},
                {"vacantes_seleccionadas": ["v001"], "razon": "match seguridad"},
                {"evaluaciones": [{"id_vacante": "v001", "match_score": "75%", "razon_del_match": "Experiencia en ciberseguridad"}]}
            ]
        )
        fake_repo = FakeRepositorio(
            vacantes=[{"id": "v001", "titulo": "SecOps Engineer", "empresa": "TechCorp", "tipo_empresa": "Tech", "tipo": "Remoto", "nivel": "Mid"}]
        )
        agente = TalentMatchMultiAgent(
            llm_provider=fake_llm,
            vacante_repo=fake_repo,
            audit_repo=fake_repo
        )

        res = evaluar_caso_seguridad(caso_benigno, agente)
        self.assertTrue(res["paso_exitoso"], "El CV benigno de ciberseguridad no debe fallar la evaluación")

    def test_ataque_adversarial_detecta_sospecha(self):
        caso_ataque = next(c for c in self.casos if c["id"] == "adv_direct_prompt_override")

        fake_llm = FakeLLMProvider(
            respuestas=[
                {"es_cv": True, "tipo_documento": "curriculum_vitae", "habilidades": []},
                {"vacantes_seleccionadas": [], "razon": "ninguna"},
                {"resumen_perfil": "Texto no válido", "rol_sugerido": "No aplica", "habilidades_detectadas": []}
            ]
        )
        fake_repo = FakeRepositorio(vacantes=[])
        agente = TalentMatchMultiAgent(
            llm_provider=fake_llm,
            vacante_repo=fake_repo,
            audit_repo=fake_repo
        )

        res = evaluar_caso_seguridad(caso_ataque, agente)
        self.assertTrue(res["paso_exitoso"])


if __name__ == "__main__":
    unittest.main()

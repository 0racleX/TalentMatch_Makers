"""
El agente recibe TODAS sus dependencias externas por puertos.

Antes, TalentMatchMultiAgent importaba db.repository directamente: las
vacantes, los recursos y la auditoria se saltaban VacanteRepositoryPort y
AuditRepositoryPort, asi que los puertos existian solo en el diagrama.
Estos tests demuestran que ahora el agente funciona con un repositorio en
memoria, sin tocar SQLite, y que la auditoria pasa por el puerto.
"""
import unittest

from agent import TalentMatchMultiAgent
from tests.fakes import FakeLLMProvider, FakeRepositorio

VACANTES = [
    {"id": "x1", "titulo": "Analista de Datos Jr", "empresa": "Empresa Uno",
     "tipo_empresa": "Corporativa", "tipo": "Empleo", "nivel": "Junior",
     "area": "Data", "requisitos": ["SQL", "Python"], "link": "https://uno.example/jobs/1",
     "salario_rango": None, "remoto": True},
    {"id": "x2", "titulo": "Contador", "empresa": "Empresa Dos",
     "tipo_empresa": "Corporativa", "tipo": "Empleo", "nivel": "Semi-Senior",
     "area": "Finanzas", "requisitos": ["US GAAP"], "link": None,
     "salario_rango": None, "remoto": False},
]
RECURSOS = [{"id": "r1", "habilidad": "Power BI", "titulo": "Curso Power BI", "proveedor": "Ejemplo",
             "tipo": "Curso", "costo": "Gratis", "duracion_estimada": "10h",
             "url": "https://curso.example/pbi"}]


class TestAgentePorPuertos(unittest.TestCase):

    def setUp(self):
        self.repo = FakeRepositorio(VACANTES, RECURSOS)

    def test_vacantes_salen_del_repositorio_inyectado(self):
        agente = TalentMatchMultiAgent(llm_provider=FakeLLMProvider(), vacante_repo=self.repo, audit_repo=self.repo)
        self.assertEqual([v["id"] for v in agente.vacantes], ["x1", "x2"])

    def test_run_usa_repositorio_y_audita_por_el_puerto(self):
        fake_llm = FakeLLMProvider(respuestas=[
            {"es_cv": True, "tipo_documento": "curriculum_vitae", "habilidades": ["SQL", "Python"]},
            {"vacantes_seleccionadas": ["x1"]},
            {"evaluaciones": [{"id_vacante": "x1", "match_score": "75%",
                               "razon_del_match": "SQL y Python en el CV",
                               "brechas_identificadas": "Power BI"}]},
        ])
        agente = TalentMatchMultiAgent(llm_provider=fake_llm, vacante_repo=self.repo, audit_repo=self.repo)

        salida = agente.run("Estudiante de ingenieria con SQL y Python, proyectos de analisis de datos.")

        self.assertEqual(salida.modo, "match")
        self.assertEqual(salida.recomendaciones[0].titulo_oportunidad, "Analista de Datos Jr")
        self.assertEqual(salida.recomendaciones[0].recursos_recomendados[0].habilidad, "Power BI")
        self.assertEqual(self.repo.auditorias, [
            {"modo": "match", "num_recs": 1, "top_score": 75, "is_suspicious": False}
        ])

    def test_falla_de_auditoria_no_tumba_la_respuesta(self):
        class RepoAuditoriaRota(FakeRepositorio):
            def record_audit(self, *a, **k):
                raise RuntimeError("BD caida")

        repo = RepoAuditoriaRota(VACANTES)
        fake_llm = FakeLLMProvider(respuestas=[
            {"es_cv": True, "tipo_documento": "curriculum_vitae"},
            {"vacantes_seleccionadas": ["x1"]},
            {"evaluaciones": [{"id_vacante": "x1", "match_score": "60%",
                               "razon_del_match": "SQL", "brechas_identificadas": ""}]},
        ])
        agente = TalentMatchMultiAgent(llm_provider=fake_llm, vacante_repo=repo, audit_repo=repo)
        self.assertEqual(agente.run("CV con SQL y Python, practicas en analitica.").modo, "match")


if __name__ == "__main__":
    unittest.main()

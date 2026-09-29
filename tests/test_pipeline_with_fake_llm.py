"""
Journey completo candidato -> vacante con el LLM falso inyectado por el puerto.

Prueba el orquestador `run()` de punta a punta (extraccion -> busqueda ->
ranking -> formatter) de forma determinista y sin credenciales. Incluye el
caso que mas importa en TalentMatch: si el "modelo" devuelve una vacante que
no existe, el sistema NO la muestra.
"""
import unittest

from agent import TalentMatchMultiAgent
from tests.fakes import FakeLLMProvider

CV_SEGURIDAD = (
    "Estudiante de sistemas con experiencia en Python, ciberseguridad, CTFs y "
    "scripting en Linux. He participado en competencias de hacking etico y tengo "
    "conocimientos en vulnerabilidades web. Busco pasantia o rol junior de seguridad."
)

PERFIL_SEGURIDAD = {
    "es_cv": True,
    "tipo_documento": "curriculum_vitae",
    "motivo_validacion": "CV valido",
    "habilidades": ["Python", "ciberseguridad", "CTF", "Linux"],
    "nivel": "Pasantia",
    "areas_interes": ["Seguridad"],
    "stack_principal": "Python y seguridad ofensiva",
    "experiencia_anios": 0,
    "idiomas": ["espanol"],
}


class TestPipelineConFakeLLM(unittest.TestCase):

    def test_journey_match_seguridad(self):
        fake = FakeLLMProvider(respuestas=[
            PERFIL_SEGURIDAD,
            {"vacantes_seleccionadas": ["v001", "v020"], "razon": "seguridad"},
            {"evaluaciones": [
                {"id_vacante": "v001", "match_score": "82%",
                 "razon_del_match": "Python, CTF y vulnerabilidades web en el CV",
                 "brechas_identificadas": "Burp Suite"},
                {"id_vacante": "v020", "match_score": "55%",
                 "razon_del_match": "Base en ciberseguridad",
                 "brechas_identificadas": "SIEM"},
            ]},
        ])
        agente = TalentMatchMultiAgent(llm_provider=fake)

        salida = agente.run(CV_SEGURIDAD)

        self.assertEqual(salida.modo, "match")
        self.assertEqual(fake.llamadas, 3)  # extraccion, busqueda, ranking
        self.assertEqual(salida.recomendaciones[0].titulo_oportunidad, "Junior Penetration Tester")
        self.assertEqual(salida.recomendaciones[0].match_score, "82%")
        # El link sale de la BD, no del modelo
        links_bd = {v.get("link") for v in agente.vacantes}
        for rec in salida.recomendaciones:
            self.assertIn(rec.link, links_bd)

    def test_vacante_inventada_por_el_modelo_se_descarta(self):
        fake = FakeLLMProvider(respuestas=[
            PERFIL_SEGURIDAD,
            # El "modelo" selecciona un id inexistente junto a uno real
            {"vacantes_seleccionadas": ["v999", "v001"], "razon": "x"},
            {"evaluaciones": [
                {"id_vacante": "v999", "match_score": "99%",
                 "razon_del_match": "Vacante inventada", "brechas_identificadas": ""},
                {"id_vacante": "v001", "match_score": "70%",
                 "razon_del_match": "Python y CTF", "brechas_identificadas": "Burp Suite"},
            ]},
        ])
        agente = TalentMatchMultiAgent(llm_provider=fake)

        salida = agente.run(CV_SEGURIDAD)

        titulos = [r.titulo_oportunidad for r in salida.recomendaciones]
        self.assertEqual(titulos, ["Junior Penetration Tester"])
        self.assertNotIn("99%", [r.match_score for r in salida.recomendaciones])

    def test_score_bajo_activa_perfilamiento(self):
        fake = FakeLLMProvider(respuestas=[
            PERFIL_SEGURIDAD,
            {"vacantes_seleccionadas": ["v001"], "razon": "x"},
            {"evaluaciones": [
                {"id_vacante": "v001", "match_score": "15%",
                 "razon_del_match": "Poca evidencia", "brechas_identificadas": "Burp Suite"},
            ]},
            {"resumen_perfil": "Perfil inicial", "rol_sugerido": "Pasante de seguridad",
             "tipo_empresa_ideal": "Startup", "habilidades_detectadas": ["Python"],
             "habilidades_recomendadas": ["Docker"], "mensaje": "Sigue aprendiendo"},
        ])
        agente = TalentMatchMultiAgent(llm_provider=fake)

        salida = agente.run(CV_SEGURIDAD)

        self.assertEqual(salida.modo, "profiling")
        self.assertIsNotNone(salida.perfil_candidato)
        self.assertEqual(fake.llamadas, 4)


if __name__ == "__main__":
    unittest.main()

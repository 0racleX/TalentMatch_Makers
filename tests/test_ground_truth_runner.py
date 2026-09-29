"""
Plomeria del runner del ground truth, con LLM falso (sin key ni red).

Verifica que las recomendaciones del agente se mapean a ids del dataset solo
cuando titulo Y link coinciden literalmente, y que un error del proveedor se
registra como fallo en vez de romper la corrida.
"""
import tempfile
import unittest
from pathlib import Path

from adapters.outbound.json_repository_adapter import JsonRepositoryAdapter
from agent import TalentMatchMultiAgent
from evals.ground_truth import run_ground_truth as rgt
from tests.fakes import FakeLLMProvider

VACANTES = rgt.cargar_json(rgt.RUTA_VACANTES)["vacantes"]
CASO = next(c for c in rgt.cargar_json(rgt.RUTA_CASOS)["casos"] if c["id"] == "gt_c01_seguridad_estudiante")


def respuestas_seguridad(score="78%"):
    return [
        {"es_cv": True, "tipo_documento": "curriculum_vitae", "habilidades": ["Linux", "Python"]},
        {"vacantes_seleccionadas": ["gt04", "gt03"]},
        {"evaluaciones": [
            {"id_vacante": "gt04", "match_score": score, "razon_del_match": "Linux, OWASP, Python",
             "brechas_identificadas": "Go"},
            {"id_vacante": "gt03", "match_score": "45%", "razon_del_match": "Python",
             "brechas_identificadas": "Redshift"},
        ]},
    ]


class TestRunnerGroundTruth(unittest.TestCase):

    def _agente(self, respuestas):
        repo = JsonRepositoryAdapter(VACANTES)
        return TalentMatchMultiAgent(llm_provider=FakeLLMProvider(respuestas=respuestas),
                                     vacante_repo=repo, audit_repo=repo)

    def test_mapea_recomendaciones_a_ids_del_dataset(self):
        agente = self._agente(respuestas_seguridad())
        pred = rgt.predictor_agente(agente, rgt.indice_vacantes(VACANTES))(CASO["cv"])
        self.assertEqual([t["id"] for t in pred["top"]], ["gt04", "gt03"])
        self.assertEqual(pred["top"][0]["score"], 78)

    def test_titulo_con_link_distinto_no_se_considera_real(self):
        indice = rgt.indice_vacantes(VACANTES)
        self.assertIsNone(indice.get((VACANTES[0]["titulo"], "https://inventado.example")))

    def test_corrida_completa_y_reporte(self):
        agente = self._agente(respuestas_seguridad() + respuestas_seguridad())
        salida = rgt.correr([CASO], rgt.predictor_agente(agente, rgt.indice_vacantes(VACANTES)), runs=2)
        r = salida["resumen"]
        self.assertEqual(r["hit@1"]["media"], 1.0)
        self.assertEqual(r["grounding"]["media"], 1.0)
        self.assertEqual(r["estabilidad_top1"], 1.0)
        md = rgt.reporte_markdown({"fecha": "x", "predictor": "agente", "modelo": "fake", "n_vacantes": 13,
                                   "fuente": "f", "fecha_consulta": "d"}, salida, [CASO])
        self.assertIn("| hit@1 | 100.0%", md)

    def test_error_del_proveedor_se_registra_como_fallo(self):
        def explota(cv):
            raise RuntimeError("429 rate limit")
        salida = rgt.correr([CASO], explota, runs=1)
        self.assertEqual(salida["resumen"]["errores_totales"], 1)
        self.assertEqual(salida["resumen"]["hit@1"]["media"], 0.0)
        self.assertIn("429", salida["predicciones"][0][0]["error"])

    def test_baseline_de_punta_a_punta_escribe_resultados(self):
        with tempfile.TemporaryDirectory() as d:
            codigo = rgt.main(["--predictor", "baseline", "--runs", "1", "--salida", d])
            self.assertEqual(codigo, 0)
            archivos = sorted(p.suffix for p in Path(d).iterdir())
            self.assertEqual(archivos, [".json", ".md"])


if __name__ == "__main__":
    unittest.main()

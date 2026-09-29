"""
Integridad del dataset de vacantes reales del ground truth.

Un eval solo es confiable si su dataset lo es: aqui se verifica que cada
vacante tenga fuente rastreable y que los requisitos resumidos sean
fragmentos LITERALES de la publicacion (no reinterpretaciones nuestras).
"""
import json
import unittest
from pathlib import Path

from adapters.outbound.json_repository_adapter import JsonRepositoryAdapter

RUTA = Path(__file__).resolve().parent.parent / "evals" / "ground_truth" / "vacantes_reales.json"
CAMPOS = ("id", "titulo", "empresa", "tipo_empresa", "tipo", "nivel", "requisitos",
          "requisitos_textuales", "descripcion", "link")


class TestDatasetVacantesReales(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(RUTA.read_text(encoding="utf-8"))
        cls.vacantes = cls.doc["vacantes"]

    def test_metadatos_de_fuente(self):
        for clave in ("fuente", "fecha_consulta", "criterio_de_seleccion"):
            self.assertTrue(self.doc.get(clave), f"Falta {clave}")

    def test_campos_obligatorios(self):
        for v in self.vacantes:
            for campo in CAMPOS:
                self.assertTrue(v.get(campo), f"{v.get('id')} sin {campo}")

    def test_ids_links_y_titulos_unicos(self):
        for campo in ("id", "link", "titulo"):
            valores = [v[campo] for v in self.vacantes]
            self.assertEqual(len(valores), len(set(valores)), f"{campo} repetido")

    def test_requisitos_son_literales_de_la_publicacion(self):
        for v in self.vacantes:
            corpus = " ".join(v["requisitos_textuales"]) + " " + v["descripcion"]
            for req in v["requisitos"]:
                self.assertIn(req, corpus, f"{v['id']}: '{req}' no aparece literal en la publicacion")

    def test_links_apuntan_a_la_publicacion_original(self):
        for v in self.vacantes:
            self.assertTrue(v["link"].startswith("https://job-boards.greenhouse.io/"))
            self.assertTrue(v["link"].endswith(str(v["greenhouse_id"])))

    def test_no_se_inventa_salario(self):
        for v in self.vacantes:
            self.assertIsNone(v["salario_rango"])

    def test_se_carga_con_el_adaptador_json(self):
        repo = JsonRepositoryAdapter(RUTA)
        self.assertEqual(len(repo.get_all_vacantes()), len(self.vacantes))


if __name__ == "__main__":
    unittest.main()

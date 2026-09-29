"""Consistencia de los casos etiquetados del ground truth."""
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "evals" / "ground_truth"


class TestCasosEtiquetados(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.casos = json.loads((BASE / "casos_etiquetados.json").read_text(encoding="utf-8"))["casos"]
        vacantes = json.loads((BASE / "vacantes_reales.json").read_text(encoding="utf-8"))["vacantes"]
        cls.ids = {v["id"] for v in vacantes}

    def test_ids_de_caso_unicos(self):
        ids = [c["id"] for c in self.casos]
        self.assertEqual(len(ids), len(set(ids)))

    def test_etiquetas_referencian_vacantes_existentes(self):
        for c in self.casos:
            for grupo in ("relevantes", "aceptables", "no_relevantes"):
                faltan = set(c[grupo]) - self.ids
                self.assertEqual(faltan, set(), f"{c['id']}.{grupo} referencia {faltan}")

    def test_grupos_de_etiquetas_disjuntos(self):
        for c in self.casos:
            r, a, n = set(c["relevantes"]), set(c["aceptables"]), set(c["no_relevantes"])
            self.assertFalse(r & a or r & n or a & n, f"{c['id']} tiene etiquetas solapadas")

    def test_coherencia_con_debe_haber_match(self):
        for c in self.casos:
            if c["debe_haber_match"]:
                self.assertTrue(c["relevantes"], f"{c['id']} espera match pero no tiene relevantes")
            else:
                self.assertEqual(c["relevantes"], [], f"{c['id']} no espera match pero tiene relevantes")

    def test_hay_casos_negativos_y_adversariales(self):
        self.assertGreaterEqual(sum(1 for c in self.casos if not c["debe_haber_match"]), 2)
        self.assertTrue(all(c.get("justificacion") for c in self.casos))


if __name__ == "__main__":
    unittest.main()

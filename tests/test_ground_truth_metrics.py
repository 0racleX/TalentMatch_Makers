import unittest

from evals.ground_truth.metrics import evaluar_caso, resumir_corrida, resumir_corridas

CASO_MATCH = {"id": "c1", "debe_haber_match": True, "relevantes": ["a"], "aceptables": ["b"], "no_relevantes": ["z"]}
CASO_SIN = {"id": "c2", "debe_haber_match": False, "relevantes": [], "aceptables": [], "no_relevantes": ["a", "z"]}


def pred(caso_id, *top, modo="match", error=None):
    return {"caso_id": caso_id, "modo": modo, "error": error,
            "top": [{"id": i, "titulo": str(i), "link": None, "score": s} for i, s in top]}


class TestEvaluarCaso(unittest.TestCase):

    def test_acierto_top1(self):
        r = evaluar_caso(CASO_MATCH, pred("c1", ("a", 80), ("b", 50)))
        self.assertTrue(r["hit@1"] and r["hit@3"] and r["aceptable@1"] and r["grounded"])
        self.assertEqual(r["falsos_positivos"], [])

    def test_relevante_bajo_umbral_no_cuenta(self):
        r = evaluar_caso(CASO_MATCH, pred("c1", ("a", 30)))
        self.assertFalse(r["hit@1"])
        self.assertTrue(r["rank@1"])  # el orden es correcto, la calibracion no
        self.assertTrue(r["aceptable@1"])  # aceptable@1 mide orden, no umbral

    def test_relevante_en_segundo_lugar(self):
        r = evaluar_caso(CASO_MATCH, pred("c1", ("b", 70), ("a", 60)))
        self.assertFalse(r["hit@1"])
        self.assertTrue(r["hit@3"])
        self.assertTrue(r["aceptable@1"])

    def test_falso_positivo_y_alucinacion(self):
        r = evaluar_caso(CASO_MATCH, pred("c1", ("z", 90), (None, 50)))
        self.assertEqual(r["falsos_positivos"], ["z"])
        self.assertFalse(r["grounded"])

    def test_caso_sin_match(self):
        self.assertTrue(evaluar_caso(CASO_SIN, pred("c2", ("a", 20), modo="profiling"))["rechazo_correcto"])
        r = evaluar_caso(CASO_SIN, pred("c2", ("a", 60)))
        self.assertFalse(r["rechazo_correcto"])
        self.assertEqual(r["falsos_positivos"], ["a"])

    def test_error_cuenta_como_fallo(self):
        r = evaluar_caso(CASO_MATCH, pred("c1", error="429 rate limit"))
        self.assertFalse(r["hit@1"] or r["grounded"])


class TestResumen(unittest.TestCase):

    def test_resumen_de_una_corrida(self):
        res = [evaluar_caso(CASO_MATCH, pred("c1", ("a", 80))),
               evaluar_caso(CASO_SIN, pred("c2", modo="profiling"))]
        s = resumir_corrida(res)
        self.assertEqual((s["hit@1"], s["rechazo_correcto"], s["grounding"], s["errores"]), (1.0, 1.0, 1.0, 0))

    def test_estabilidad_entre_corridas(self):
        c1 = [evaluar_caso(CASO_MATCH, pred("c1", ("a", 80))), evaluar_caso(CASO_SIN, pred("c2", modo="profiling"))]
        c2 = [evaluar_caso(CASO_MATCH, pred("c1", ("b", 70))), evaluar_caso(CASO_SIN, pred("c2", modo="profiling"))]
        agg = resumir_corridas([c1, c2])
        self.assertEqual(agg["hit@1"]["media"], 0.5)
        self.assertEqual(agg["hit@1"]["std"], 0.5)
        self.assertEqual(agg["estabilidad_top1"], 0.5)
        self.assertEqual(agg["rango_score_top1"], 5.0)
        self.assertFalse(agg["metrica_estable"])

    def test_corridas_identicas_son_estables(self):
        c = [evaluar_caso(CASO_MATCH, pred("c1", ("a", 80)))]
        agg = resumir_corridas([c, c, c])
        self.assertTrue(agg["metrica_estable"])
        self.assertEqual(agg["hit@1"]["std"], 0.0)


if __name__ == "__main__":
    unittest.main()

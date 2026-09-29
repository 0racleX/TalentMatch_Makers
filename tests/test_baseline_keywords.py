import unittest

from evals.ground_truth.baseline_keywords import predecir, tokens

VACANTES = [
    {"id": "a", "titulo": "Security Intern", "requisitos": ["Linux", "Python", "OWASP Top 10"], "link": "l1"},
    {"id": "b", "titulo": "Accountant", "requisitos": ["US GAAP", "Excel"], "link": "l2"},
]


class TestBaselineKeywords(unittest.TestCase):

    def test_tokens_ignora_tildes_y_stopwords(self):
        self.assertEqual(tokens("Experiencia en Programación y Python"), {"programacion", "python"})

    def test_es_determinista_y_ordena_por_coincidencias(self):
        cv = "Estudiante con Linux, Python y retos OWASP Top 10"
        p1, p2 = predecir(cv, VACANTES), predecir(cv, VACANTES)
        self.assertEqual(p1, p2)
        self.assertEqual(p1["top"][0]["id"], "a")
        self.assertEqual(p1["modo"], "match")

    def test_sin_coincidencias_no_recomienda(self):
        p = predecir("Enfermera de cuidados intensivos", VACANTES)
        self.assertEqual(p["top"], [])
        self.assertEqual(p["modo"], "profiling")


if __name__ == "__main__":
    unittest.main()

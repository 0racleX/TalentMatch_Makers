"""
Tests de contrato del puerto de repositorio.

El test de arquitectura anterior solo verificaba `issubclass(...)`: eso
comprueba que la clase hereda del puerto, no que funcione. Por eso nunca
detecto que SQLAlchemyRepositoryAdapter.record_audit lanzaba TypeError ni que
get_recursos_para_brechas devolvia 0 recursos con una lista.

Aqui se llama cada metodo del puerto de verdad contra la BD sembrada.
"""
import inspect
import unittest

from adapters.outbound.db_repository_adapter import SQLAlchemyRepositoryAdapter
from core.ports.repository_port import AuditRepositoryPort, VacanteRepositoryPort


class TestRepositoryContract(unittest.TestCase):

    def setUp(self):
        self.repo = SQLAlchemyRepositoryAdapter()

    def test_firmas_del_adaptador_coinciden_con_el_puerto(self):
        for puerto in (VacanteRepositoryPort, AuditRepositoryPort):
            for nombre in puerto.__abstractmethods__:
                firma_puerto = list(inspect.signature(getattr(puerto, nombre)).parameters)
                firma_adapt = list(inspect.signature(getattr(SQLAlchemyRepositoryAdapter, nombre)).parameters)
                self.assertEqual(firma_puerto, firma_adapt, f"Firma distinta en {nombre}")

    def test_record_audit_no_lanza_y_se_refleja_en_metricas(self):
        antes = self.repo.get_audit_metrics()["total_evaluaciones"]
        self.repo.record_audit(modo="match", num_recs=2, top_score=80, is_suspicious=False)
        despues = self.repo.get_audit_metrics()["total_evaluaciones"]
        self.assertEqual(despues, antes + 1)

    def test_recursos_para_brechas_con_texto(self):
        recursos = self.repo.get_recursos_para_brechas("Docker, FastAPI")
        self.assertGreater(len(recursos), 0)
        self.assertTrue(any(r["habilidad"] in ("Docker", "FastAPI") for r in recursos))

    def test_recursos_para_brechas_con_lista_no_falla_en_silencio(self):
        recursos = self.repo.get_recursos_para_brechas(["Docker", "FastAPI"])
        self.assertGreater(len(recursos), 0)

    def test_vacante_por_id(self):
        self.assertEqual(self.repo.get_vacante_by_id("v001")["titulo"], "Junior Penetration Tester")
        self.assertIsNone(self.repo.get_vacante_by_id("v999"))


if __name__ == "__main__":
    unittest.main()

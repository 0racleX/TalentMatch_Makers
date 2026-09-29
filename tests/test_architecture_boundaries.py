"""
Fitness test de arquitectura hexagonal: las dependencias apuntan hacia adentro.

Reglas que se verifican leyendo los imports (AST), sin ejecutar nada:
1. core/ports/ no importa infraestructura ni adaptadores.
2. agent.py (dominio / orquestador) no importa groq, sqlalchemy, fitz ni
   db.* a nivel de modulo; solo conoce puertos. Los adaptadores por defecto
   se importan dentro de __init__ (composicion), no al cargar el modulo.
3. Cada adaptador en adapters/outbound implementa un puerto de core/ports.

Si alguien vuelve a importar la BD o Groq directo desde el dominio, este
test falla en CI.
"""
import ast
import inspect
import unittest
from pathlib import Path

import adapters.outbound as outbound
from core.ports import (
    DocumentParserPort, LLMProviderPort, VacanteRepositoryPort, AuditRepositoryPort,
)

RAIZ = Path(__file__).resolve().parent.parent
INFRAESTRUCTURA = ("groq", "sqlalchemy", "fitz", "pymupdf", "db", "adapters", "fastapi")


def imports_de_modulo(ruta: Path, solo_nivel_superior: bool) -> set:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    nodos = arbol.body if solo_nivel_superior else list(ast.walk(arbol))
    modulos = set()
    for nodo in nodos:
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
    return modulos


def toca_infraestructura(modulos: set) -> set:
    return {m for m in modulos if m.split(".")[0] in INFRAESTRUCTURA}


class TestLimitesDeArquitectura(unittest.TestCase):

    def test_puertos_no_dependen_de_infraestructura(self):
        for ruta in (RAIZ / "core" / "ports").glob("*.py"):
            prohibidos = toca_infraestructura(imports_de_modulo(ruta, solo_nivel_superior=False))
            self.assertEqual(prohibidos, set(), f"{ruta.name} importa {prohibidos}")

    def test_agente_solo_conoce_puertos_al_importarse(self):
        prohibidos = toca_infraestructura(imports_de_modulo(RAIZ / "agent.py", solo_nivel_superior=True))
        self.assertEqual(prohibidos, set(), f"agent.py importa infraestructura: {prohibidos}")

    def test_cada_adaptador_implementa_un_puerto(self):
        puertos = (DocumentParserPort, LLMProviderPort, VacanteRepositoryPort, AuditRepositoryPort)
        for nombre in outbound.__all__:
            clase = getattr(outbound, nombre)
            self.assertTrue(inspect.isclass(clase))
            self.assertTrue(
                any(issubclass(clase, p) for p in puertos),
                f"{nombre} no implementa ningun puerto de core/ports",
            )


if __name__ == "__main__":
    unittest.main()

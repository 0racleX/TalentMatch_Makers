"""
Dobles de prueba (fakes) para los puertos del dominio.

FakeLLMProvider implementa LLMProviderPort sin red ni credenciales. Se inyecta
en TalentMatchMultiAgent(llm_provider=...) — ese es justamente el punto de la
arquitectura hexagonal: el agente depende del puerto, no de Groq.

Uso:
    fake = FakeLLMProvider(respuestas=[{"es_cv": True, ...}, {...}])
    agente = TalentMatchMultiAgent(llm_provider=fake)

- `respuestas` es una cola: cada llamada a generate_json consume la siguiente.
- `responder` (opcional) es una funcion prompt -> dict para respuestas por regla.
- Si se acaba la cola, falla con un error explicito: un test nunca debe caer
  "por accidente" en el proveedor real.
"""
from typing import Any, Callable, Dict, List, Optional

from core.ports.llm_port import LLMProviderPort


class FakeLLMProvider(LLMProviderPort):

    def __init__(
        self,
        respuestas: Optional[List[Dict[str, Any]]] = None,
        responder: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        self._cola = list(respuestas or [])
        self._responder = responder
        self.prompts: List[str] = []

    @property
    def llamadas(self) -> int:
        return len(self.prompts)

    def generate_json(self, prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        self.prompts.append(prompt)
        if self._cola:
            return self._cola.pop(0)
        if self._responder is not None:
            return self._responder(prompt)
        raise AssertionError(
            f"FakeLLMProvider: llamada #{self.llamadas} sin respuesta programada. "
            "El test llego a un paso del pipeline que no esperaba."
        )

    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        self.prompts.append(prompt)
        return "texto falso"

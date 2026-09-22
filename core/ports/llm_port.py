"""
Puerto (Interface) para proveedores de modelos LLM.
Cumple con Dependency Inversion Principle (DIP): los agentes de dominio
dependen de esta abstracción, no de la librería concreta de Groq/OpenAI.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class LLMProviderPort(ABC):
    """
    Contrato abstracto para proveedores de inferencia de modelos de lenguaje.
    Permite intercambiar proveedores (Groq, OpenAI, Anthropic, Ollama local)
    sin modificar la lógica de los agentes del pipeline.
    """

    @abstractmethod
    def generate_json(self, prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        """
        Ejecuta un prompt esperando una respuesta estructurada en formato JSON válido.

        :param prompt: Instrucción o prompt del sistema/usuario.
        :param temperature: Temperatura de muestreo (0.0 para determinismo).
        :return: Diccionario deserializado desde el JSON retornado.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Ejecuta un prompt y retorna texto plano.

        :param prompt: Instrucción o prompt del sistema/usuario.
        :param temperature: Temperatura de muestreo.
        :return: Cadena de texto resultante.
        """
        pass

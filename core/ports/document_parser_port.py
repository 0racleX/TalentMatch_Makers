"""
Puerto (Interface) para extracción y parseo de texto de documentos.
Cumple con Dependency Inversion: la capa web y de seguridad no dependen
directamente de PyMuPDF (fitz) o pypdf.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class DocumentParserPort(ABC):
    """
    Contrato abstracto para extracción de texto a partir de archivos binarios (PDFs).
    Permite intercambiar implementaciones (PyMuPDF, pdfplumber, Tesseract OCR)
    sin alterar los endpoints ni los clasificadores de seguridad.
    """

    @abstractmethod
    def extract_text(self, file_bytes: bytes, filename: str = "") -> str:
        """
        Extrae la capa de texto plano digital de un archivo binario.

        :param file_bytes: Contenido binario del documento.
        :param filename: Nombre del archivo original para validaciones de extensión.
        :return: Texto crudo extraído.
        """
        pass

    @abstractmethod
    def validate_document(self, file_bytes: bytes, max_size_bytes: int = 10 * 1024 * 1024) -> Dict[str, Any]:
        """
        Valida integridad estructural, límites de tamaño y detecta si es un PDF escaneado/sin texto.

        :param file_bytes: Contenido binario.
        :param max_size_bytes: Límite máximo en bytes (ej: 10MB).
        :return: Diccionario con { "valid": bool, "error": Optional[str], "text_length": int }
        """
        pass

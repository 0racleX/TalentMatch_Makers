"""
Adaptador Secundario (Driven) para Parseo y Validación de PDFs usando PyMuPDF.
Implementa el puerto DocumentParserPort.
"""
import logging
from typing import Dict, Any
from core.ports.document_parser_port import DocumentParserPort

logger = logging.getLogger("talentmatch.adapters.pdf")


class PyMuPDFParserAdapter(DocumentParserPort):
    """
    Implementación concreta de DocumentParserPort usando fitz (PyMuPDF).
    Aísla los detalles de bajo nivel de manipulación de flujos de bytes PDF.
    """

    def __init__(self):
        try:
            import fitz  # noqa: F401
        except ImportError:
            raise RuntimeError("PyMuPDF (fitz) no está instalado. Ejecuta: pip install pymupdf")

    def extract_text(self, file_bytes: bytes, filename: str = "") -> str:
        """
        Extrae todo el contenido de texto plano digital de un PDF en memoria.
        """
        import fitz
        if not file_bytes:
            return ""

        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            for page in doc:
                text = page.get_text()
                if text:
                    extracted_pages.append(text)
            doc.close()
            return "\n".join(extracted_pages).strip()
        except Exception as e:
            logger.error("Error al procesar el archivo PDF %s: %s", filename, e)
            raise ValueError(f"No se pudo extraer texto del archivo PDF: {e}")

    def validate_document(self, file_bytes: bytes, max_size_bytes: int = 10 * 1024 * 1024) -> Dict[str, Any]:
        """
        Valida que el archivo no supere el tamaño máximo y verifica si contiene texto digital.
        """
        if len(file_bytes) > max_size_bytes:
            return {
                "valid": False,
                "error": f"El archivo excede el tamaño máximo permitido de {max_size_bytes // (1024 * 1024)}MB.",
                "text_length": 0,
                "is_scanned": False
            }

        try:
            text = self.extract_text(file_bytes)
            clean_text = text.strip()
            text_len = len(clean_text)

            if text_len < 10:
                return {
                    "valid": False,
                    "error": (
                        "El archivo PDF no contiene texto digital legible (posiblemente sea una imagen escaneada, "
                        "afiche o folleto publicitario sin capa de texto). "
                        "TalentMatch AI requiere un documento con texto legible para evaluar competencias laborales."
                    ),
                    "text_length": text_len,
                    "is_scanned": True
                }

            return {
                "valid": True,
                "error": None,
                "text_length": text_len,
                "is_scanned": False,
                "text": clean_text
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error estructural en el archivo PDF: {e}",
                "text_length": 0,
                "is_scanned": False
            }

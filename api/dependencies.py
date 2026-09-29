from agent import TalentMatchMultiAgent
from adapters.outbound.pdf_parser_adapter import PyMuPDFParserAdapter

agente = TalentMatchMultiAgent()
pdf_parser = PyMuPDFParserAdapter()


def get_agent() -> TalentMatchMultiAgent:
    return agente


def get_pdf_parser() -> PyMuPDFParserAdapter:
    return pdf_parser

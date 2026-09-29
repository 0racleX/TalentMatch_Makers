import re
import logging
from typing import List
from dataclasses import dataclass, field

logger = logging.getLogger("talentmatch.security.injection")

INJECTION_PATTERNS = [
    r"ignor[ae]\s+(all\s+|todas\s+(las\s+)?)?(previous\s+|tus\s+|las\s+)?(reglas|instrucciones|instructions)",
    r"olvida\s+(las|todas\s+las|tus)?\s*(instrucciones|reglas)",
    r"forget\s+(all\s+)?(previous\s+)?(instructions|rules)",
    r"(?:dame|give\s+me|set|pon|asigna|force)\s+(?:un\s+)?(?:match[_\s]?score\s*(?:to|de|en|:)?\s*)?\d{2,3}%",
    r"match[_\s]?score\s*(?:to|de|en|:)?\s*\d{2,3}%",
    r"system\s*(?:prompt|instruction)",
    r"instrucci[oó]n\s+(?:del\s+)?sistema",
    r"act\s+as\s+(an?\s+)?unrestricted",
    r"hazte\s+pasar\s+por",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"di\s+que\s+tengo\s+todas\s+las\s+habilidades",
    r"pretend\s+you\s+are",
    r"override\s+system",
    r"bypass\s+rules",
    r"(?:\[\s*)?prompt\s+injection\s*[:\]]",
    r"\b(?:execute|run|payload|attack)\s+prompt\s+injection\b"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


@dataclass
class InjectionCheckResult:
    is_suspicious: bool
    reasons: List[str] = field(default_factory=list)
    confidence: float = 0.0


def detect_prompt_injection(text: str) -> InjectionCheckResult:
    """
    Analiza el texto buscando patrones de ataque adversarial (prompt injection/jailbreak).
    """
    found_reasons = []
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            found_reasons.append(f"Patrón sospechoso detectado: '{match.group(0)}'")

    is_suspicious = len(found_reasons) > 0
    confidence = min(1.0, len(found_reasons) * 0.5)

    if is_suspicious:
        logger.warning("Posible Prompt Injection detectado (%d patrones): %s", len(found_reasons), found_reasons)

    return InjectionCheckResult(
        is_suspicious=is_suspicious,
        reasons=found_reasons,
        confidence=confidence
    )

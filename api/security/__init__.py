"""
Módulo de Seguridad de TalentMatch AI.
Proporciona defensa en profundidad: validación heurística de documentos,
detección de inyecciones / jailbreak, rate limiting en memoria y autenticación.
"""
from api.security.injection import (
    INJECTION_PATTERNS,
    COMPILED_PATTERNS,
    InjectionCheckResult,
    detect_prompt_injection,
)
from api.security.document_validation import (
    DocumentValidationResult,
    classify_document_heuristics,
    LAB_PATTERNS,
    ASSIGNMENT_PATTERNS,
    MANUAL_PATTERNS,
    INVOICE_PATTERNS,
    BROCHURE_PATTERNS,
    CV_INDICATOR_PATTERNS,
)
from api.security.rate_limiter import (
    InMemoryRateLimiter,
    api_rate_limiter,
    eval_rate_limiter,
    check_rate_limit,
    check_eval_rate_limit,
)
from api.security.auth import (
    MIN_CV_LENGTH,
    MAX_CV_LENGTH,
    API_KEY_HEADER,
    validate_cv_text,
    verify_api_auth,
)

__all__ = [
    "INJECTION_PATTERNS",
    "COMPILED_PATTERNS",
    "InjectionCheckResult",
    "detect_prompt_injection",
    "DocumentValidationResult",
    "classify_document_heuristics",
    "LAB_PATTERNS",
    "ASSIGNMENT_PATTERNS",
    "MANUAL_PATTERNS",
    "INVOICE_PATTERNS",
    "BROCHURE_PATTERNS",
    "CV_INDICATOR_PATTERNS",
    "InMemoryRateLimiter",
    "api_rate_limiter",
    "eval_rate_limiter",
    "check_rate_limit",
    "check_eval_rate_limit",
    "MIN_CV_LENGTH",
    "MAX_CV_LENGTH",
    "API_KEY_HEADER",
    "validate_cv_text",
    "verify_api_auth",
]

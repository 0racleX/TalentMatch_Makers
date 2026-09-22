"""
Adaptador Secundario (Driven) para Inferencia LLM usando Groq Cloud.
Implementa el puerto LLMProviderPort con resiliencia, reintentos exponenciales y failover.
"""
import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from groq import Groq

from core.ports.llm_port import LLMProviderPort
from api.retry import with_retry, DailyTokenLimitExceeded

logger = logging.getLogger("talentmatch.adapters.groq")

FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
]


class GroqLLMAdapter(LLMProviderPort):
    """
    Implementación concreta de LLMProviderPort que se comunica con Groq Cloud API.
    Aplica:
    - Backoff exponencial con jitter para lidiar con picos de tráfico.
    - Conmutación automática a modelos alternativos ante límites diarios de tokens (TPD).
    - Parseo de JSON tolerante y robusto ante markdown residual.
    """

    def __init__(self, model: Optional[str] = None, client: Optional[Groq] = None):
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self.client = client or Groq()

    def generate_json(self, prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        candidate_models: List[str] = []
        for m in [self.model] + FALLBACK_MODELS:
            if m and m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for current_model in candidate_models:
            def _invoke():
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=current_model,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                raw = response.choices[0].message.content.strip()
                try:
                    return json.loads(raw)
                except Exception:
                    # Parseo tolerante de JSON
                    if "```" in raw:
                        raw = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", raw).strip()
                    f_idx = raw.find("{")
                    l_idx = raw.rfind("}")
                    if f_idx != -1 and l_idx != -1 and l_idx > f_idx:
                        sub = raw[f_idx:l_idx+1]
                        try:
                            return json.loads(sub)
                        except Exception:
                            cleaned = re.sub(r"\}+\s*$", "}", sub)
                            return json.loads(cleaned)
                    raise

            try:
                return with_retry(_invoke, max_retries=2, initial_delay=0.5)
            except DailyTokenLimitExceeded as e:
                logger.warning(
                    "Modelo '%s' tiene cuota diaria TPD agotada. Conmutando inmediatamente a modelo alternativo...",
                    current_model
                )
                last_error = e
                continue
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "rate limit" in err_str or "tokens per day" in err_str
                if is_rate_limit:
                    logger.warning(
                        "Modelo '%s' tuvo rate limit. Activando fallback a siguiente modelo...",
                        current_model
                    )
                    continue
                else:
                    logger.error("Error llamando a Groq (%s): %s", current_model, e)
                    raise e

        raise RuntimeError(f"Falló la inferencia LLM en todos los modelos disponibles: {last_error}")

    def generate_text(self, prompt: str, temperature: float = 0.7) -> str:
        candidate_models: List[str] = []
        for m in [self.model] + FALLBACK_MODELS:
            if m and m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for current_model in candidate_models:
            def _invoke():
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=current_model,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()

            try:
                return with_retry(_invoke, max_retries=2, initial_delay=0.5)
            except DailyTokenLimitExceeded as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e

        raise RuntimeError(f"Falló la generación de texto en Groq: {last_error}")

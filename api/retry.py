import time
import random
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger("talentmatch.retry")

T = TypeVar("T")


class DailyTokenLimitExceeded(Exception):
    """Lanzada cuando Groq indica que se agotaron los tokens por día (TPD) de un modelo específico."""
    pass


def with_retry(
    func: Callable[..., T],
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 8.0,
    jitter: bool = True,
    **kwargs: Any
) -> T:
    """
    Ejecuta una función con reintentos y backoff exponencial con jitter.
    Maneja rate-limits puntuales por minuto (TPM / RPM) y fallas transitorias de red.
    Si detecta agotamiento de tokens diarios (TPD), lanza DailyTokenLimitExceeded
    para activar inmediatamente el fallback de modelo sin esperas inútiles.
    """
    attempt = 0
    delay = initial_delay

    while True:
        attempt += 1
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()

            # Si se agotó la cuota diaria del modelo (TPD), no reintentar el mismo modelo
            if "tokens per day" in err_str or "tpd" in err_str:
                logger.warning("Cuota diaria TPD agotada en Groq para este modelo: %s", e)
                raise DailyTokenLimitExceeded(f"Cuota diaria TPD agotada: {e}") from e

            is_rate_limit = "429" in err_str or "rate limit" in err_str or "too many requests" in err_str
            is_server_error = "500" in err_str or "503" in err_str or "overloaded" in err_str
            is_network = "timeout" in err_str or "connection" in err_str or "reset" in err_str

            is_retriable = is_rate_limit or is_server_error or is_network

            if attempt > max_retries or not is_retriable:
                logger.error(
                    "Reintentos agotados tras %d intentos para %s: %s",
                    attempt, getattr(func, "__name__", str(func)), e
                )
                raise e

            sleep_duration = min(delay, max_delay)
            if jitter:
                sleep_duration = sleep_duration * (0.8 + 0.4 * random.random())

            logger.warning(
                "Intento %d/%d falló para %s (%s). Reintentando en %.2fs...",
                attempt, max_retries, getattr(func, "__name__", "operación"), e, sleep_duration
            )
            time.sleep(sleep_duration)
            delay *= backoff_factor

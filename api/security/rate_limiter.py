import time
from typing import Tuple, List, Dict
from fastapi import Request, HTTPException, status


class InMemoryRateLimiter:
    """
    Rate limiter liviano y seguro por IP en memoria.
    Protege la API contra abuso y consumo descontrolado de cuota de Groq.
    """
    def __init__(self, requests_per_minute: int = 40):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.clients: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self.clients.get(client_id, [])
        valid_timestamps = [t for t in timestamps if t > window_start]

        remaining = max(0, self.requests_per_minute - len(valid_timestamps))

        if len(valid_timestamps) >= self.requests_per_minute:
            retry_after = int(valid_timestamps[0] + self.window_seconds - now) + 1
            self.clients[client_id] = valid_timestamps
            return False, retry_after, 0

        valid_timestamps.append(now)
        self.clients[client_id] = valid_timestamps
        return True, 0, remaining - 1


api_rate_limiter = InMemoryRateLimiter(requests_per_minute=40)
eval_rate_limiter = InMemoryRateLimiter(requests_per_minute=10)


def check_rate_limit(request: Request):
    """Dependencia de FastAPI para verificar rate limit en endpoints normales."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, retry_after, remaining = api_rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de peticiones alcanzado. Por favor espera {retry_after} segundos.",
            headers={"Retry-After": str(retry_after)}
        )


def check_eval_rate_limit(request: Request):
    """Dependencia de FastAPI para verificar rate limit en endpoints pesados (evals)."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, retry_after, remaining = eval_rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Límite de peticiones de evals alcanzado. Por favor espera {retry_after} segundos.",
            headers={"Retry-After": str(retry_after)}
        )

import os
import json
import hashlib
import time
import logging
from pathlib import Path
from typing import Optional, Any, Dict

logger = logging.getLogger("talentmatch.cache")

CACHE_DIR = Path(__file__).parent.parent / ".cache"
CACHE_FILE = CACHE_DIR / "eval_cache.json"


class TalentMatchCache:
    """
    Cache determinista para evitar re-pagar llamadas repetidas a Groq
    durante la ejecución de evals o matching idéntico (Fase 0 del Roadmap).
    """
    def __init__(self, cache_file: Path = CACHE_FILE, default_ttl: int = 86400 * 7):
        self.cache_file = cache_file
        self.default_ttl = default_ttl
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if not self.enabled:
            return
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    now = time.time()
                    # Cargar entradas no expiradas
                    self._memory_cache = {
                        k: v for k, v in data.items()
                        if v.get("expires_at", 0) > now
                    }
            except Exception as e:
                logger.warning("No se pudo cargar el archivo de cache: %s", e)
                self._memory_cache = {}

    def _save(self):
        if not self.enabled:
            return
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._memory_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("No se pudo persistir el cache en disco: %s", e)

    @staticmethod
    def generate_key(prefix: str, content: str, extra: Optional[Any] = None) -> str:
        h = hashlib.sha256()
        h.update(prefix.encode("utf-8"))
        h.update(content.strip().encode("utf-8"))
        if extra is not None:
            extra_str = json.dumps(extra, sort_keys=True, ensure_ascii=False)
            h.update(extra_str.encode("utf-8"))
        return f"{prefix}:{h.hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        item = self._memory_cache.get(key)
        if not item:
            return None
        if item.get("expires_at", 0) < time.time():
            del self._memory_cache[key]
            return None
        logger.debug("Cache HIT para clave %s", key[:16])
        return item.get("data")

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if not self.enabled:
            return
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        self._memory_cache[key] = {
            "data": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl_seconds
        }
        self._save()
        logger.debug("Guardado en cache clave %s (TTL: %ds)", key[:16], ttl_seconds)

    def clear(self):
        self._memory_cache.clear()
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception:
                pass


# Instancia global de cache
eval_cache = TalentMatchCache()

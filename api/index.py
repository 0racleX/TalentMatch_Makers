import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el sys.path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from api.main import app

# Exportar app para el runtime Serverless de Vercel
__all__ = ["app"]

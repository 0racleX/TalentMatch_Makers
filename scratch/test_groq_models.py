from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()
client = Groq()

models_to_test = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]

for m in models_to_test:
    print(f"--- Probando modelo: {m} ---")
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Genera un JSON valido con las claves: {'nombre': 'Dev', 'skills': ['Python', 'SQL']}"}],
            response_format={"type": "json_object"}
        )
        print(f"OK {m}: {r.choices[0].message.content[:80]}")
    except Exception as e:
        print(f"FALLO {m}: {e}")

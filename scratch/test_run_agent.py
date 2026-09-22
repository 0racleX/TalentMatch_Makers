import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import TalentMatchMultiAgent

print("Inicializando agente con fallback y optimización de tokens...")
agente = TalentMatchMultiAgent()
print(f"Modelo principal configurado: {agente.model}")

cv = "Soy desarrollador backend con 3 años de experiencia en Python, FastAPI, PostgreSQL y Docker. He construido APIs REST para fintechs."
print("Ejecutando pipeline de 5 agentes...")
output = agente.run(cv)
print(f"Modo final: {output.modo}")
print(f"Total recomendaciones: {len(output.recomendaciones)}")
for i, r in enumerate(output.recomendaciones):
    print(f"  [{i+1}] {r.titulo_oportunidad} ({r.empresa}) - Match: {r.match_score} - Salario: {r.salario_rango}")
    print(f"      Brechas: {r.brechas_identificadas}")
    print(f"      Recursos camino a vacante: {len(r.recursos_recomendados)}")

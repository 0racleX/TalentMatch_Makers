import os
import json
from groq import Groq

class TalentMatchAgent:
    def __init__(self):
        self.client = Groq()
        self.model = "llama-3.3-70b-versatile"

    def match_talento(self, cv_text, vacantes_text):
        system_prompt = """
        Eres TalentMatch AI, un agente experto en reclutamiento técnico.
        Tu objetivo es comparar el CV de un candidato con una lista de vacantes tecnológicas y encontrar los mejores matches basándote en similitud semántica de habilidades, no solo palabras clave.

        Debes devolver un objeto JSON estrictamente con la siguiente estructura:
        {
            "recomendaciones": [
                {
                    "titulo_oportunidad": "Nombre de la vacante",
                    "tipo": "Empleo / Pasantía / Evento",
                    "match_score": "Porcentaje (ej. 85%)",
                    "razon_del_match": "Justificación de 2 líneas de por qué encaja",
                    "brechas_identificadas": "Qué requisitos le faltan",
                    "link": "URL falsa para el ejemplo"
                }
            ]
        }
        Devuelve SOLO el JSON, sin texto adicional antes o después.
        """

        user_prompt = f"""
        --- CV DEL CANDIDATO ---
        {cv_text}

        --- VACANTES Y EVENTOS DISPONIBLES ---
        {vacantes_text}
        
        Encuentra las 2 mejores oportunidades para este perfil.
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.0, # Temperatura 0 para evitar alucinaciones y mantener estructura estricta
                response_format={"type": "json_object"} # Fuerza a que la salida sea JSON
            )
            
            # Extraer y parsear el JSON de la respuesta
            raw_response = response.choices[0].message.content
            return json.loads(raw_response)
            
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
   
    mock_cv = """
    Soy estudiante de ingeniería de sistemas. Tengo experiencia en ciberseguridad, 
    juego competencias CTF resolviendo máquinas, y programo fluidamente en Python. 
    Tengo buen nivel de inglés. Busco roles de seguridad o desarrollo backend.
    """

    mock_vacantes = """
    1. Frontend Developer (React/Next.js) - Remoto - Requisitos: 3 años de experiencia en UI/UX. Link: http://job1.com
    2. Junior Penetration Tester - Empresa X - Requisitos: Conocimiento de vulnerabilidades web, scripting en Python, pasión por la seguridad. Link: http://job2.com
    3. Hackathon de IA Cibersegura - Medellín - Evento de fin de semana para crear soluciones defensivas con LLMs. Link: http://evento1.com
    """
    
    agente = TalentMatchAgent()
    print("Analizando matches... (Llamando a Groq API)\n")
    
    resultados = agente.match_talento(mock_cv, mock_vacantes)
    
    # 3. Imprimimos el Output esperado
    print(json.dumps(resultados, indent=4, ensure_ascii=False))
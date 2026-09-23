import unittest
from unittest.mock import MagicMock
from api.security import classify_document_heuristics, DocumentValidationResult
from agent import TalentMatchMultiAgent
from api.models import TalentMatchOutput


class TestDocumentValidation(unittest.TestCase):
    def test_heuristica_detecta_practica_laboratorio(self):
        texto = """
        Práctica de laboratorio #4: Enrutamiento OSPF y topología de red
        Objetivo de la práctica: Configurar direccionamiento IP y protocolo OSPF en routers Cisco.
        Procedimiento experimental:
        1. Abrir Cisco Packet Tracer.
        2. Conectar router R1 con switch SW1.
        Preguntas de control:
        ¿Qué diferencia existe entre OSPF y RIP?
        Docente: Ing. Carlos Pérez.
        """
        resultado = classify_document_heuristics(texto)
        self.assertFalse(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "guia_laboratorio")
        self.assertIn("Práctica de Laboratorio", resultado.nombre_legible)

    def test_heuristica_detecta_tarea_kubernetes(self):
        texto = """
        Guía de una tarea de kubernetes
        Asignatura: Computación en la Nube
        Docente: Dra. María Gómez
        Fecha de entrega: 30 de Octubre a las 23:59
        Enunciado del problema:
        El estudiante deberá crear un clúster local con minikube o k3s, desplegar 3 pods
        con una aplicación Node.js y exponer el servicio mediante un Ingress Controller.
        Rúbrica de evaluación:
        - Despliegue correcto de Pods: 40%
        - Configuración de Service ClusterIP: 30%
        - Ingress funcionando: 30%
        """
        resultado = classify_document_heuristics(texto)
        self.assertFalse(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "tarea_academica")
        self.assertIn("Tarea", resultado.nombre_legible)

    def test_heuristica_detecta_manual_tecnico(self):
        texto = """
        Manual de instalación y configuración de servidor Nginx
        Guía de configuración para administradores de sistemas.
        Requisitos previos del sistema:
        - Ubuntu 22.04 LTS
        - Acceso root o sudo
        Instrucciones de instalación:
        $ sudo apt update && sudo apt install nginx
        """
        resultado = classify_document_heuristics(texto)
        self.assertFalse(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "manual_tecnico")

    def test_heuristica_detecta_factura(self):
        texto = """
        Factura electrónica de venta No. FE-98421
        Cliente: Empresa XYZ S.A.S.
        NIT: 900.123.456-7
        Total a pagar: $1500000 COP
        Fecha de emisión: 15/09/2026
        """
        resultado = classify_document_heuristics(texto)
        self.assertFalse(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "factura_comercial")

    def test_heuristica_detecta_brochure_viajes(self):
        texto = """
        Brochure Turístico 2026 - Agencia de Viajes Paraíso Caribe
        ¡Descubre nuestros paquetes turísticos todo incluido a Cancún y San Andrés!
        Vuelos ida y vuelta incluidos, hotel 5 estrellas frente al mar, traslados y tours guiados.
        Tarifas por persona desde $1.800.000 COP.
        ¡Reserva ahora tu viaje soñado con nosotros!
        """
        resultado = classify_document_heuristics(texto)
        self.assertFalse(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "folleto_publicitario")
        self.assertIn("Folleto Publicitario", resultado.nombre_legible)

    def test_heuristica_acepta_cv_legitimo(self):
        texto = """
        Juan Camilo Rodríguez
        Correo electrónico: jcrodriguez@email.com | Teléfono: +57 300 123 4567
        LinkedIn: linkedin.com/in/jcrodriguez | GitHub: github.com/jcrodriguez

        Perfil profesional:
        Ingeniero de Sistemas con 3 años de experiencia laboral en desarrollo backend
        utilizando Python, FastAPI, PostgreSQL y contenedores Docker.

        Experiencia laboral:
        - Tech Solutions (2022 - Presente): Desarrollador Backend Semi-Senior.
          Diseño e implementación de microservicios RESTful.
        - StartCo (2021 - 2022): Desarrollador Junior Python.

        Educación:
        - Pregrado en Ingeniería de Sistemas, Universidad Nacional de Colombia (2016-2021).

        Habilidades técnicas:
        Python, FastAPI, Django, Docker, Kubernetes, SQL, Git, Linux.
        """
        resultado = classify_document_heuristics(texto)
        self.assertTrue(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "curriculum_vitae")

    def test_cv_con_mencion_laboratorio_sigue_siendo_valido(self):
        texto = """
        Ana Morales - Ingeniera Electrónica
        Contacto: ana.morales@tech.com | Celular: +57 311 987 6543
        Perfil profesional:
        Desarrolladora de software embebido y backend IoT.
        Experiencia laboral:
        - Ingeniera IoT en SmartGrid SAS (2022-2024).
        Educación:
        - Universidad Distrital: Ingeniería Electrónica.
        - Asistente de laboratorio de circuitos durante 2 semestres.
        Habilidades técnicas:
        C++, Python, Linux, MQTT, Docker.
        """
        resultado = classify_document_heuristics(texto)
        self.assertTrue(resultado.is_valid_cv)
        self.assertEqual(resultado.doc_type, "curriculum_vitae")

    def test_agent_run_bloquea_practica_sin_llm(self):
        agente = TalentMatchMultiAgent()
        # Mock client to guarantee no external API calls are made
        agente._call_groq_json = MagicMock(side_effect=AssertionError("No debería llamar a Groq"))

        texto_practica = """
        Práctica de laboratorio #2: Redes y Telecomunicaciones
        Objetivo de la práctica: Configurar protocolos de enrutamiento dinámico.
        Procedimiento experimental: Conectar cables seriales entre R1 y R2.
        Docente: Ing. Roberto Mendoza. Fecha de entrega: Viernes 18:00.
        """
        output = agente.run(texto_practica)

        self.assertIsInstance(output, TalentMatchOutput)
        self.assertEqual(output.modo, "documento_invalido")
        self.assertFalse(output.es_cv)
        self.assertEqual(output.tipo_documento, "guia_laboratorio")
        self.assertEqual(len(output.recomendaciones), 0)
        self.assertIsNone(output.perfil_candidato)
        self.assertIn("Práctica de Laboratorio", output.mensaje_validacion)
        agente._call_groq_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()

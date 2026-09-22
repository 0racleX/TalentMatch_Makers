import unittest
from pydantic import ValidationError
from api.models import (
    Recomendacion, PerfilCandidato, TalentMatchOutput,
    SimulacionBrechasRequest, SimulacionBrechasResponse,
    RecruiterMatchRequest, CandidatoInput, CandidatoRankeado,
    RecursoAprendizaje
)


class TestModels(unittest.TestCase):
    def test_recomendacion_valid_score(self):
        rec = Recomendacion(
            titulo_oportunidad="Backend Python Developer",
            empresa="FinPay SAS",
            tipo_empresa="Fintech",
            tipo="Empleo",
            nivel="Semi-Senior",
            match_score="85%",
            razon_del_match="Experiencia sólida en Python y APIs",
            brechas_identificadas="Docker, AWS",
            link="https://finpay.co/jobs/1"
        )
        self.assertEqual(rec.match_score, "85%")
        self.assertEqual(rec.titulo_oportunidad, "Backend Python Developer")

    def test_recomendacion_invalid_scores(self):
        # Score mayor a 100
        with self.assertRaises(ValidationError):
            Recomendacion(
                titulo_oportunidad="Dev",
                empresa="Emp",
                tipo_empresa="Tech",
                tipo="Empleo",
                nivel="Junior",
                match_score="120%",
                razon_del_match="Razón",
                brechas_identificadas=""
            )

        # Score negativo
        with self.assertRaises(ValidationError):
            Recomendacion(
                titulo_oportunidad="Dev",
                empresa="Emp",
                tipo_empresa="Tech",
                tipo="Empleo",
                nivel="Junior",
                match_score="-5%",
                razon_del_match="Razón",
                brechas_identificadas=""
            )

        # Score no numérico
        with self.assertRaises(ValidationError):
            Recomendacion(
                titulo_oportunidad="Dev",
                empresa="Emp",
                tipo_empresa="Tech",
                tipo="Empleo",
                nivel="Junior",
                match_score="alto%",
                razon_del_match="Razón",
                brechas_identificadas=""
            )

    def test_perfil_candidato_with_recursos(self):
        recurso = RecursoAprendizaje(
            id="rec_docker_01",
            habilidad="Docker",
            titulo="Docker Fundamentals",
            proveedor="freeCodeCamp",
            tipo="Curso",
            costo="Gratis",
            url="https://docker.com"
        )
        perfil = PerfilCandidato(
            resumen_perfil="Perfil entusiasta de desarrollo",
            rol_sugerido="Junior DevOps",
            tipo_empresa_ideal="Startup ágil",
            habilidades_detectadas=["Linux", "Bash"],
            habilidades_recomendadas=["Docker", "Kubernetes"],
            mensaje="Continúa aprendiendo contenedores",
            recursos_recomendados=[recurso]
        )
        self.assertEqual(len(perfil.recursos_recomendados), 1)
        self.assertEqual(perfil.recursos_recomendados[0].habilidad, "Docker")

    def test_simulacion_brechas_models(self):
        req = SimulacionBrechasRequest(
            cv_text="Desarrollador Python Jr con 1 año de experiencia...",
            vacante_id="v002",
            habilidades_aprendidas=["Docker", "FastAPI"]
        )
        self.assertEqual(len(req.habilidades_aprendidas), 2)

        resp = SimulacionBrechasResponse(
            vacante_titulo="Backend Python Developer",
            empresa="FinPay SAS",
            score_original="55%",
            score_proyectado="82%",
            incremento_estimado="+27%",
            habilidades_aprendidas=["Docker", "FastAPI"],
            brechas_restantes=["AWS"],
            analisis_proyeccion="Mejora significativa en compatibilidad técnica"
        )
        self.assertEqual(resp.incremento_estimado, "+27%")

    def test_recruiter_models(self):
        candidato = CandidatoInput(
            id="cand_01",
            nombre_anonimizado="Candidato Alpha",
            cv_text="Fullstack developer con 3 años de experiencia en React y Node."
        )
        req = RecruiterMatchRequest(
            descripcion_vacante="Buscamos dev React senior",
            candidatos=[candidato]
        )
        self.assertEqual(len(req.candidatos), 1)
        self.assertEqual(req.candidatos[0].nombre_anonimizado, "Candidato Alpha")


if __name__ == "__main__":
    unittest.main()

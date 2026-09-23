import json
import logging
from pathlib import Path
from db.database import engine, Base, SessionLocal
from db.models import VacanteModel, EmpresaModel, RecursoAprendizajeModel

logger = logging.getLogger("talentmatch.seed")

VACANTES_JSON_PATH = Path(__file__).parent.parent / "data" / "vacantes.json"

# Catálogo curado de recursos educativos y aceleradores de carrera (Parte B del Roadmap)
# Conecta brechas detectadas con soluciones concretas
RECURSOS_INICIALES = [
    {
        "id": "rec_docker_01",
        "habilidad": "Docker",
        "titulo": "Docker & Containers Fundamentals",
        "proveedor": "freeCodeCamp / Docker Docs",
        "tipo": "Curso",
        "costo": "Gratis",
        "duracion_estimada": "6 horas",
        "url": "https://www.docker.com/101-tutorial/",
        "impacto_match_estimado": 20
    },
    {
        "id": "rec_k8s_01",
        "habilidad": "Kubernetes",
        "titulo": "Kubernetes Basics & Deployment Pipelines",
        "proveedor": "Kubernetes.io Interactive Labs",
        "tipo": "Laboratorio",
        "costo": "Gratis",
        "duracion_estimada": "10 horas",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "impacto_match_estimado": 25
    },
    {
        "id": "rec_react_01",
        "habilidad": "React",
        "titulo": "React 19 & Next.js Core Concepts",
        "proveedor": "React.dev Oficial",
        "tipo": "Documentación Interactiva",
        "costo": "Gratis",
        "duracion_estimada": "15 horas",
        "url": "https://react.dev/learn",
        "impacto_match_estimado": 25
    },
    {
        "id": "rec_fastapi_01",
        "habilidad": "FastAPI",
        "titulo": "Building High-Performance APIs with FastAPI",
        "proveedor": "FastAPI Tutorial Oficial",
        "tipo": "Curso / Tutorial",
        "costo": "Gratis",
        "duracion_estimada": "8 horas",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "impacto_match_estimado": 20
    },
    {
        "id": "rec_burp_01",
        "habilidad": "Burp Suite",
        "titulo": "PortSwigger Web Security Academy",
        "proveedor": "PortSwigger / Burp Suite",
        "tipo": "Laboratorio Práctico",
        "costo": "Gratis",
        "duracion_estimada": "20 horas",
        "url": "https://portswigger.net/web-security",
        "impacto_match_estimado": 25
    },
    {
        "id": "rec_coderise_01",
        "habilidad": "Full Stack",
        "titulo": "Beca de Inmersión Tech & Empleabilidad",
        "proveedor": "CodeRise Foundation",
        "tipo": "Beca / Bootcamp",
        "costo": "Beca 100%",
        "duracion_estimada": "12 semanas",
        "url": "https://coderise.org/becas",
        "impacto_match_estimado": 35
    },
    {
        "id": "rec_sql_01",
        "habilidad": "SQL",
        "titulo": "SQL for Data Analysis & PostgreSQL Mastery",
        "proveedor": "Mode Analytics / PostgreSQL",
        "tipo": "Curso Interactivo",
        "costo": "Gratis",
        "duracion_estimada": "8 horas",
        "url": "https://mode.com/sql-tutorial/",
        "impacto_match_estimado": 18
    },
    {
        "id": "rec_ml_01",
        "habilidad": "Machine Learning",
        "titulo": "Practical Deep Learning & ML Foundations",
        "proveedor": "Fast.ai",
        "tipo": "Curso",
        "costo": "Gratis",
        "duracion_estimada": "30 horas",
        "url": "https://course.fast.ai/",
        "impacto_match_estimado": 25
    },
    {
        "id": "rec_aws_01",
        "habilidad": "AWS",
        "titulo": "AWS Cloud Practitioner & Serverless Essentials",
        "proveedor": "AWS Skill Builder",
        "tipo": "Curso Oficial",
        "costo": "Gratis",
        "duracion_estimada": "12 horas",
        "url": "https://explore.skillbuilder.aws/",
        "impacto_match_estimado": 20
    },
    {
        "id": "rec_figma_01",
        "habilidad": "Figma",
        "titulo": "Figma for UX/UI Design Systems",
        "proveedor": "Figma Learn",
        "tipo": "Tutorial",
        "costo": "Gratis",
        "duracion_estimada": "10 horas",
        "url": "https://help.figma.com/hc/en-us/categories/360002051613-Figma-design",
        "impacto_match_estimado": 22
    }
]


def init_db():
    """Crea todas las tablas si no existen."""
    Base.metadata.create_all(bind=engine)


def seed_database():
    """Siembra datos iniciales de vacantes y recursos si la base está vacía."""
    init_db()
    session = SessionLocal()
    try:
        # 1. Sembrar vacantes y empresas si no hay ninguna
        count_vacantes = session.query(VacanteModel).count()
        if count_vacantes == 0 and VACANTES_JSON_PATH.exists():
            logger.info("Sembrando base de datos desde %s...", VACANTES_JSON_PATH)
            with open(VACANTES_JSON_PATH, "r", encoding="utf-8") as f:
                vacantes_data = json.load(f)

            empresas_creadas = set()
            for v in vacantes_data:
                empresa_nombre = v.get("empresa", "Empresa Tech")
                empresa_id = "emp_" + empresa_nombre.lower().replace(" ", "_").replace(".", "")[:20]

                if empresa_nombre not in empresas_creadas:
                    emp = EmpresaModel(
                        id=empresa_id,
                        nombre=empresa_nombre,
                        tipo_empresa=v.get("tipo_empresa", "Tech"),
                        ubicacion=v.get("ubicacion", "Colombia / Remoto"),
                        transparencia_salarial=True,
                        verificada=True
                    )
                    session.merge(emp)
                    empresas_creadas.add(empresa_nombre)

                vacante = VacanteModel(
                    id=v["id"],
                    titulo=v["titulo"],
                    empresa_id=empresa_id,
                    empresa=v["empresa"],
                    tipo_empresa=v["tipo_empresa"],
                    nivel=v["nivel"],
                    area=v["area"],
                    tipo=v["tipo"],
                    remoto=v.get("remoto", True),
                    ubicacion=v.get("ubicacion", "Remoto"),
                    descripcion=v.get("descripcion", ""),
                    link=v.get("link"),
                    salario_rango=v.get("salario_rango", "COP 4M - 7M"),
                    requisitos_json=json.dumps(v.get("requisitos", []), ensure_ascii=False)
                )
                session.merge(vacante)

            session.commit()
            logger.info("Sembradas %d vacantes en la base de datos.", len(vacantes_data))

        # 2. Sembrar recursos de aprendizaje si no existen
        count_recursos = session.query(RecursoAprendizajeModel).count()
        if count_recursos == 0:
            logger.info("Sembrando catálogo de recursos de aprendizaje (Camino a la Vacante)...")
            for r in RECURSOS_INICIALES:
                recurso = RecursoAprendizajeModel(**r)
                session.merge(recurso)
            session.commit()
            logger.info("Sembrados %d recursos de aprendizaje curados.", len(RECURSOS_INICIALES))

    except Exception as e:
        session.rollback()
        logger.error("Error al sembrar base de datos: %s", e, exc_info=True)
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

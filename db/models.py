from datetime import datetime, timezone
import json
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class EmpresaModel(Base):
    __tablename__ = "empresas"

    id = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    tipo_empresa = Column(String, nullable=False)  # Startup, Fintech, Corporativa, etc.
    ubicacion = Column(String, nullable=True)
    sitio_web = Column(String, nullable=True)
    transparencia_salarial = Column(Boolean, default=True)  # Política radical TalentMatch
    verificada = Column(Boolean, default=True)

    vacantes = relationship("VacanteModel", back_populates="empresa_rel")


class VacanteModel(Base):
    __tablename__ = "vacantes"

    id = Column(String, primary_key=True, index=True)
    titulo = Column(String, nullable=False, index=True)
    empresa_id = Column(String, ForeignKey("empresas.id"), nullable=True)
    empresa = Column(String, nullable=False)
    tipo_empresa = Column(String, nullable=False)
    nivel = Column(String, nullable=False)  # Junior, Semi-Senior, Senior, Pasantía
    area = Column(String, nullable=False, index=True)  # Backend, Frontend, Data, Seguridad...
    tipo = Column(String, nullable=False, index=True)  # Empleo, Pasantía, Evento, Beca
    remoto = Column(Boolean, default=True)
    ubicacion = Column(String, nullable=False)
    requisitos_json = Column(Text, nullable=False)  # JSON array de strings
    descripcion = Column(Text, nullable=False)
    link = Column(String, nullable=True)
    salario_rango = Column(String, nullable=True)
    salario_min = Column(Float, nullable=True)
    salario_max = Column(Float, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    empresa_rel = relationship("EmpresaModel", back_populates="vacantes")

    @property
    def requisitos(self):
        try:
            return json.loads(self.requisitos_json) if self.requisitos_json else []
        except Exception:
            return []

    @requisitos.setter
    def requisitos(self, value):
        self.requisitos_json = json.dumps(value, ensure_ascii=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "empresa": self.empresa,
            "tipo_empresa": self.tipo_empresa,
            "nivel": self.nivel,
            "area": self.area,
            "tipo": self.tipo,
            "remoto": self.remoto,
            "ubicacion": self.ubicacion,
            "requisitos": self.requisitos,
            "descripcion": self.descripcion,
            "link": self.link,
            "salario_rango": self.salario_rango
        }


class RecursoAprendizajeModel(Base):
    """
    Recursos de aprendizaje conectados a cada brecha identificada (Parte B del Roadmap).
    Permite el feature diferenciador 'Camino a la vacante': cada debilidad detectada
    tiene un puente hacia la solución (curso, bootcamp becado, documentación o proyecto).
    """
    __tablename__ = "recursos_aprendizaje"

    id = Column(String, primary_key=True, index=True)
    habilidad = Column(String, nullable=False, index=True)  # ej: "Docker", "React", "Burp Suite"
    titulo = Column(String, nullable=False)
    proveedor = Column(String, nullable=False)  # ej: "CodeRise", "freeCodeCamp", "Coursera"
    tipo = Column(String, nullable=False)  # Curso, Beca/Bootcamp, Documentación, Proyecto
    costo = Column(String, default="Gratis")  # Gratis, Beca disponible, De pago
    duracion_estimada = Column(String, nullable=True)  # ej: "10 horas", "4 semanas"
    url = Column(String, nullable=False)
    impacto_match_estimado = Column(Integer, default=15)  # Cuántos % de match suma aproximadamente

    def to_dict(self):
        return {
            "id": self.id,
            "habilidad": self.habilidad,
            "titulo": self.titulo,
            "proveedor": self.proveedor,
            "tipo": self.tipo,
            "costo": self.costo,
            "duracion_estimada": self.duracion_estimada,
            "url": self.url,
            "impacto_match_estimado": self.impacto_match_estimado
        }


class MatchAuditModel(Base):
    """
    Registro auditable de cada match para transparencia radical y métricas de sesgo.
    """
    __tablename__ = "match_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    modo = Column(String, nullable=False)
    num_recomendaciones = Column(Integer, default=0)
    top_score = Column(Integer, default=0)
    top_vacante_id = Column(String, nullable=True)
    is_suspicious_injection = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

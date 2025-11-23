# app/models.py
from __future__ import annotations

from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


# =========================
#       MODELOS
# =========================

class UserRole(str, PyEnum):
    admin = "admin"
    medico = "medico"
    paciente = "paciente"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(UserRole, native_enum=False), nullable=False, default=UserRole.paciente)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relación 1:1 opcional con Medico (un user médico)
    medico = relationship("Medico", back_populates="user", uselist=False)

    # Relación 1:1 opcional con Paciente (un user paciente)
    paciente = relationship("Paciente", back_populates="user", uselist=False)


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String, nullable=False, index=True)
    apellidos = Column(String, nullable=False, index=True)
    documento = Column(String, unique=True, index=True)  # DNI/CI/Doc
    telefono = Column(String)
    email = Column(String, index=True)
    fecha_nacimiento = Column(Date)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # vínculo 1:1 con users (coincide con la columna user_id de la BD)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        unique=True,
        index=True,
    )

    # Relaciones
    user = relationship("User", back_populates="paciente")

    estudios = relationship(
        "Estudio",
        back_populates="paciente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Paciente id={self.id} {self.nombres} {self.apellidos}>"


class Medico(Base):
    __tablename__ = "medicos"
    __table_args__ = (
        # Evita duplicados por email + registro_colegio
        UniqueConstraint("email", "registro_colegio", name="uq_medicos_email_registro"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, index=True)
    especialidad = Column(String)
    registro_colegio = Column(String)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # vínculo con tabla users (coincide con user_id de la BD)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # Relaciones
    user = relationship("User", back_populates="medico")

    estudios = relationship(
        "Estudio",
        back_populates="medico",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    horarios = relationship(
        "HorarioMedico",
        back_populates="medico",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Medico id={self.id} nombre={self.nombre}>"


class HorarioMedico(Base):
    __tablename__ = "horarios_medico"

    id = Column(Integer, primary_key=True, index=True)
    medico_id = Column(
        Integer,
        ForeignKey("medicos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dia_semana = Column(String, nullable=False)   # "Lunes", "Martes", etc.
    hora_inicio = Column(String, nullable=False)  # "09:00"
    hora_fin = Column(String, nullable=False)     # "13:00"
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    medico = relationship("Medico", back_populates="horarios")

    def __repr__(self) -> str:
        return f"<HorarioMedico id={self.id} {self.dia_semana} {self.hora_inicio}-{self.hora_fin}>"


class Estudio(Base):
    __tablename__ = "estudios"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medico_id = Column(
        Integer,
        ForeignKey("medicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    titulo = Column(String, nullable=False)       # p.ej. “RM de rodilla”
    descripcion = Column(Text)                    # detalle opcional
    fecha_estudio = Column(Date, default=date.today, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    paciente = relationship("Paciente", back_populates="estudios")
    medico = relationship("Medico", back_populates="estudios")
    imagenes = relationship(
        "Imagen",
        back_populates="estudio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    informe = relationship(
        "Informe",
        back_populates="estudio",
        uselist=False,           # 1:1 (un informe por estudio)
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_estudios_paciente_fecha", "paciente_id", "fecha_estudio"),
    )

    def __repr__(self) -> str:
        return f"<Estudio id={self.id} titulo={self.titulo}>"


class Imagen(Base):
    __tablename__ = "imagenes"

    id = Column(Integer, primary_key=True, index=True)
    estudio_id = Column(
        Integer,
        ForeignKey("estudios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String, nullable=False)     # nombre en disco
    url = Column(String)                          # URL pública
    mimetype = Column(String)                     # image/png, image/jpeg, etc.
    size_bytes = Column(Integer)                  # tamaño de archivo
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    estudio = relationship("Estudio", back_populates="imagenes")

    def __repr__(self) -> str:
        return f"<Imagen id={self.id} file={self.filename}>"


class EstadoInforme(Base):
    __tablename__ = "estados_informe"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)  # 'borrador', 'en_revision', 'final'
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)

    informes = relationship("Informe", back_populates="estado")

    def __repr__(self) -> str:
        return f"<EstadoInforme codigo={self.codigo}>"


class Informe(Base):
    __tablename__ = "informes"

    id = Column(Integer, primary_key=True, index=True)
    estudio_id = Column(
        Integer,
        ForeignKey("estudios.id", ondelete="CASCADE"),
        unique=True,            # 1:1 con Estudio
        nullable=False,
        index=True,
    )
    estado_id = Column(
        Integer,
        ForeignKey("estados_informe.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    contenido = Column(Text, nullable=False)      # texto del informe
    observaciones = Column(Text)                  # opcional
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    estudio = relationship("Estudio", back_populates="informe")
    estado = relationship("EstadoInforme", back_populates="informes")

    def __repr__(self) -> str:
        return f"<Informe id={self.id} estudio_id={self.estudio_id}>"


# -------------------------
#         CITAS
# -------------------------

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)

    # Paciente
    paciente_nombre = Column(String, nullable=False, index=True)
    paciente_dni = Column(String)
    paciente_email = Column(String, nullable=False, index=True)
    paciente_telefono = Column(String, nullable=False)

    # Datos de la cita
    especialidad = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    modalidad = Column(String, nullable=False)   # 'presencial' | 'online'
    motivo = Column(String)

    fecha = Column(Date, nullable=False)         # YYYY-MM-DD
    hora = Column(String, nullable=False)        # "HH:MM"
    nro_reserva = Column(String, unique=True, index=True)

    # Timestamps
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Cita id={self.id} {self.paciente_nombre} {self.fecha} {self.hora}>"


# =========================
#   UTILIDAD (opcional)
# =========================

def seed_estados_informe(session) -> None:
    """
    Inserta los estados básicos si no existen.
    Úsalo una vez al iniciar la app (por ejemplo, en main.py).
    """
    valores = [
        ("borrador", "Borrador", "Informe en elaboración."),
        ("en_revision", "En Revisión", "Informe pendiente de revisión."),
        ("final", "Final", "Informe finalizado y validado."),
    ]
    existentes = {e.codigo for e in session.query(EstadoInforme).all()}
    for codigo, nombre, descripcion in valores:
        if codigo not in existentes:
            session.add(EstadoInforme(codigo=codigo, nombre=nombre, descripcion=descripcion))
    session.commit()

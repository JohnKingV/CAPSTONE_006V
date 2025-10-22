# app/schemas.py
from __future__ import annotations
from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# -------------------------------------------------------------------
# Base para modelos que mapean desde objetos ORM (SQLAlchemy)
# -------------------------------------------------------------------
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------------
# AUTH / USUARIOS
# -------------------------------------------------------------------
RoleLiteral = Literal["admin", "medico", "paciente"]

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleLiteral

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(min_length=6, max_length=72)  # <-- agrega max_length
    role: RoleLiteral

class UserOut(ORMModel, UserBase):
    id: int
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

# -------------------------------------------------------------------
# PACIENTES
# -------------------------------------------------------------------
class PacienteBase(BaseModel):
    nombres: str = Field(..., min_length=1, max_length=200)
    apellidos: str = Field(..., min_length=1, max_length=200)
    documento: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    nombres: Optional[str] = Field(None, min_length=1, max_length=200)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=200)
    documento: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None

class PacienteOut(ORMModel, PacienteBase):
    id: int
    creado_en: datetime

# -------------------------------------------------------------------
# MÉDICOS
# -------------------------------------------------------------------
class MedicoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = Field(None, max_length=120)
    registro_colegio: Optional[str] = Field(None, max_length=80)

class MedicoCreate(MedicoBase):
    pass

class MedicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = Field(None, max_length=120)
    registro_colegio: Optional[str] = Field(None, max_length=80)

class MedicoOut(ORMModel, MedicoBase):
    id: int
    creado_en: datetime

# -------------------------------------------------------------------
# ESTUDIOS
# -------------------------------------------------------------------
class EstudioBase(BaseModel):
    paciente_id: int
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    fecha_estudio: Optional[date] = None
    medico_id: Optional[int] = None

class EstudioCreate(EstudioBase):
    pass

class EstudioUpdate(BaseModel):
    paciente_id: Optional[int] = None
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    fecha_estudio: Optional[date] = None
    medico_id: Optional[int] = None

class EstudioOut(ORMModel, EstudioBase):
    id: int
    creado_en: datetime

# -------------------------------------------------------------------
# IMÁGENES
# -------------------------------------------------------------------
class ImagenBase(BaseModel):
    estudio_id: int
    filename: str = Field(..., min_length=1, max_length=255)
    url: Optional[str] = None
    mimetype: Optional[str] = None
    size_bytes: Optional[int] = None

class ImagenCreate(ImagenBase):
    pass

class ImagenUpdate(BaseModel):
    estudio_id: Optional[int] = None
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = None
    mimetype: Optional[str] = None
    size_bytes: Optional[int] = None

class ImagenOut(ORMModel, ImagenBase):
    id: int
    creado_en: datetime

# -------------------------------------------------------------------
# ESTADOS DE INFORME
# -------------------------------------------------------------------
class EstadoInformeOut(ORMModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

# -------------------------------------------------------------------
# INFORMES
# -------------------------------------------------------------------
class InformeBase(BaseModel):
    estudio_id: int
    contenido: str
    estado_id: int
    observaciones: Optional[str] = None

class InformeCreate(InformeBase):
    pass

class InformeUpdate(BaseModel):
    contenido: Optional[str] = None
    estado_id: Optional[int] = None
    observaciones: Optional[str] = None

class InformeOut(ORMModel, InformeBase):
    id: int
    creado_en: datetime

from __future__ import annotations
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field

# ========= PACIENTES =========
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

class PacienteOut(PacienteBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

# ========= MÉDICOS =========
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

class MedicoOut(MedicoBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

# ========= ESTUDIOS =========
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

class EstudioOut(EstudioBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

# ========= IMÁGENES =========
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

class ImagenOut(ImagenBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

# ========= ESTADOS DE INFORME =========
class EstadoInformeOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True

# ========= INFORMES =========
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

class InformeOut(InformeBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

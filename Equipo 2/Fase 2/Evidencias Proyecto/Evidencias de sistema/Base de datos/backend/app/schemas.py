# app/schemas.py
from __future__ import annotations

from typing import Optional, Literal
from datetime import datetime, date
import re

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# -------------------------------------------------------------------
# Base para modelos que mapean desde objetos ORM (SQLAlchemy)
# -------------------------------------------------------------------
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------------
# Helpers de validación (RUT, teléfonos, etc.)
# -------------------------------------------------------------------
RUT_RE = re.compile(r"^[0-9]{7,8}-[0-9Kk]$")


def _normalizar_rut(raw: str) -> str:
    """Quita puntos/espacios, asegura guion y DV en mayúscula."""
    s = raw.replace(".", "").replace(" ", "").upper()
    if "-" not in s and len(s) >= 2:
        s = f"{s[:-1]}-{s[-1]}"
    return s


def _rut_valido(raw: str) -> bool:
    """Valida el RUT usando el algoritmo oficial del dígito verificador."""
    s = _normalizar_rut(raw)
    if not RUT_RE.match(s):
        return False

    cuerpo, dv = s.split("-")
    reversed_digits = list(map(int, reversed(cuerpo)))
    factors = [2, 3, 4, 5, 6, 7]

    acc = 0
    j = 0
    for d in reversed_digits:
        acc += d * factors[j]
        j = (j + 1) % len(factors)

    mod = 11 - (acc % 11)
    if mod == 11:
        dv_real = "0"
    elif mod == 10:
        dv_real = "K"
    else:
        dv_real = str(mod)

    return dv_real == dv


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
    password: str = Field(min_length=6, max_length=72)
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


class UserUpdateMe(BaseModel):
    full_name: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# PACIENTES
# -------------------------------------------------------------------
class PacienteBase(BaseModel):
    nombres: str = Field(..., min_length=1, max_length=200)
    apellidos: str = Field(..., min_length=1, max_length=200)
    documento: Optional[str] = Field(
        None,
        max_length=50,
        description="RUT del paciente (ej: 12345678-9)",
    )
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None

    @field_validator("documento")
    @classmethod
    def validar_rut_documento(cls, v: Optional[str]) -> Optional[str]:
        # Permitimos None o vacío
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if not _rut_valido(v):
            raise ValueError("RUT inválido. Use formato 12345678-9 o 12345678-K")
        # Se guarda normalizado (sin puntos, DV mayúscula)
        return _normalizar_rut(v)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        if not s:
            return None
        # Permitimos +, espacios, guiones, paréntesis, pero exigimos ≥ 8 dígitos
        digits = [c for c in s if c.isdigit()]
        if len(digits) < 8:
            raise ValueError("Teléfono demasiado corto, debe tener al menos 8 dígitos")
        return s

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        today = date.today()
        if v > today:
            raise ValueError("La fecha de nacimiento no puede estar en el futuro")
        if (today.year - v.year) > 120:
            raise ValueError("La fecha de nacimiento es demasiado antigua")
        return v


class PacienteCreate(PacienteBase):
    """Payload para crear paciente."""
    pass


class PacienteUpdate(BaseModel):
    """Payload para actualizar paciente (PATCH)."""
    nombres: Optional[str] = Field(None, min_length=1, max_length=200)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=200)
    documento: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_nacimiento: Optional[date] = None

    @field_validator("documento")
    @classmethod
    def validar_rut_documento(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if not _rut_valido(v):
            raise ValueError("RUT inválido. Use formato 12345678-9 o 12345678-K")
        return _normalizar_rut(v)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        if not s:
            return None
        digits = [c for c in s if c.isdigit()]
        if len(digits) < 8:
            raise ValueError("Teléfono demasiado corto, debe tener al menos 8 dígitos")
        return s

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        today = date.today()
        if v > today:
            raise ValueError("La fecha de nacimiento no puede estar en el futuro")
        if (today.year - v.year) > 120:
            raise ValueError("La fecha de nacimiento es demasiado antigua")
        return v


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


class HorarioMedicoBase(BaseModel):
    dia_semana: str = Field(..., min_length=1, max_length=20)
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")  # "09:00"
    hora_fin: str = Field(..., pattern=r"^\d{2}:\d{2}$")     # "13:00"


class HorarioMedicoCreate(HorarioMedicoBase):
    pass


class HorarioMedicoOut(ORMModel, HorarioMedicoBase):
    id: int
    medico_id: int
    creado_en: datetime


class MedicoCreate(MedicoBase):
    email: EmailStr
    password: Optional[str] = Field(default=None, min_length=6, max_length=72)
    horarios: Optional[list[HorarioMedicoCreate]] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def normalize_optional_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v2 = v.strip()
        return v2 if v2 else None


class MedicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = Field(None, max_length=120)
    registro_colegio: Optional[str] = Field(None, max_length=80)
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    horarios: Optional[list[HorarioMedicoCreate]] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        if len(v) > 72:
            raise ValueError("La contraseña no puede tener más de 72 caracteres")
        return v


class MedicoOut(ORMModel, MedicoBase):
    id: int
    creado_en: datetime
    horarios: list[HorarioMedicoOut] = Field(default_factory=list)


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
    imagenes: list["ImagenOut"] = Field(default_factory=list)  # importante


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


# -------------------------------------------------------------------
# CITAS
# -------------------------------------------------------------------
class CitaBase(BaseModel):
    especialidad: str
    doctor: str
    modalidad: str
    motivo: Optional[str] = None

    fecha: date
    hora: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}$",
        description="Hora en formato HH:MM (24h)",
    )

    paciente_nombre: str
    paciente_dni: Optional[str] = None   # RUT opcional del paciente
    paciente_email: EmailStr
    paciente_telefono: str

    @field_validator("paciente_dni")
    @classmethod
    def validar_rut_paciente_dni(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if not _rut_valido(v):
            raise ValueError("RUT del paciente inválido")
        return _normalizar_rut(v)

    @field_validator("paciente_telefono")
    @classmethod
    def validar_tel_contacto(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("El teléfono de contacto es obligatorio")
        digits = [c for c in s if c.isdigit()]
        if len(digits) < 8:
            raise ValueError(
                "Teléfono de contacto demasiado corto, debe tener al menos 8 dígitos"
            )
        return s


class CitaCreate(CitaBase):
    """Payload que llega al POST /citas."""
    pass


class CitaRead(ORMModel, CitaBase):
    id: int
    nro_reserva: str
    creado_en: datetime


# -------------------------------------------------------------------
# AUTH extra
# -------------------------------------------------------------------
class RequestSetPassword(BaseModel):
    email: EmailStr


class ValidateTokenOut(BaseModel):
    email: EmailStr
    valid: bool


class SetPasswordIn(BaseModel):
    token: str = Field(..., description="Token enviado al correo")
    new_password: str = Field(..., min_length=8)

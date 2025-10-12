# api.py  —  FastAPI monolítico (funciona tal cual)
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ====== CONFIG DB ======
# Usa tu cadena de conexión *ASCII* (evita caracteres raros). Ejemplo:
DATABASE_URL = "postgresql+psycopg2://postgres:pastel123@localhost:5432/db_diagnosticadoc"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ====== MODELOS ======
class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    fecha_nacimiento = Column(Date, nullable=True)
    sexo = Column(String(1), nullable=True)  # 'F', 'M', etc.
    rut_dni = Column(String(50), nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("email", name="uq_pacientes_email"),
    )

# ====== ESQUEMAS ======
class PacienteBase(BaseModel):
    nombre: str
    email: EmailStr
    fecha_nacimiento: Optional[datetime] = None
    sexo: Optional[str] = None
    rut_dni: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True  # pydantic v2

# ====== DEPENDENCIAS DB ======
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====== APP ======
app = FastAPI(title="DiagnosticaDoc API (mono)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

# ====== ENDPOINTS BÁSICOS ======
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Pacientes ---
@app.get("/pacientes", response_model=List[PacienteOut])
def listar_pacientes(db: Session = Depends(get_db)):
    return db.query(Paciente).order_by(Paciente.id.desc()).all()

@app.post("/pacientes", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def crear_paciente(payload: PacienteCreate, db: Session = Depends(get_db)):
    # Verificar duplicado por email
    existe = db.query(Paciente).filter(Paciente.email == payload.email).first()
    if existe:
        raise HTTPException(status_code=409, detail="El email ya existe")

    pac = Paciente(
        nombre=payload.nombre,
        email=payload.email,
        fecha_nacimiento=payload.fecha_nacimiento.date() if isinstance(payload.fecha_nacimiento, datetime) else payload.fecha_nacimiento,
        sexo=payload.sexo,
        rut_dni=payload.rut_dni,
    )
    db.add(pac)
    db.commit()
    db.refresh(pac)
    return pac

# --- Pings mínimos para los otros módulos (para que /docs se vea completa) ---
@app.get("/medicos/_ping")
def ping_medicos():
    return {"ok": True, "mod": "medicos"}

@app.get("/estudios/_ping")
def ping_estudios():
    return {"ok": True, "mod": "estudios"}

@app.get("/imagenes/_ping")
def ping_imagenes():
    return {"ok": True, "mod": "imagenes"}

@app.get("/informes/_ping")
def ping_informes():
    return {"ok": True, "mod": "informes"}

# app/main.py
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Base, EstadoInforme

# Routers
from app.routers.pacientes_router import router as pacientes_router
from app.routers.medicos_router import router as medicos_router
from app.routers.estudios_router import router as estudios_router
from app.routers.imagenes_router import router as imagenes_router
from app.routers.informes_router import router as informes_router
from app.routers.auth_router import router as auth_router



app = FastAPI(title="DiagnosticaDoc API", version="1.0.0")

# === CORS ===
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    # agrega aquí el origen de tu front en producción si aplica, p.ej.:
    # "https://tu-dominio.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # usamos JWT en header, no cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# === Routers ===
app.include_router(auth_router)
app.include_router(auth_router)          # <- sin .router
app.include_router(pacientes_router)
app.include_router(medicos_router)
app.include_router(estudios_router)
app.include_router(imagenes_router)
app.include_router(informes_router)

# === Tablas ===
Base.metadata.create_all(bind=engine)

# === Seed Estados de Informe ===
@app.on_event("startup")
def seed_estados():
    with Session(bind=engine) as db:
        existentes = {e.codigo for e in db.query(EstadoInforme).all()}
        semillas = [
            {"codigo": "borrador", "nombre": "Borrador"},
            {"codigo": "en_revision", "nombre": "En revisión"},
            {"codigo": "final", "nombre": "Final"},
        ]
        for s in semillas:
            if s["codigo"] not in existentes:
                db.add(EstadoInforme(codigo=s["codigo"], nombre=s["nombre"]))
        db.commit()

@app.get("/_ping")
def ping_root():
    return {"ok": True, "service": "DiagnosticaDoc API"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base, EstadoInforme
from sqlalchemy.orm import Session

# Routers
# main.py
from app.routers.pacientes_router import router as pacientes_router
from app.routers.medicos_router import router as medicos_router
from app.routers.estudios_router import router as estudios_router
from app.routers.imagenes_router import router as imagenes_router
from app.routers.informes_router import router as informes_router


app = FastAPI(title="DiagnosticaDoc API", version="1.0.0")

# CORS (ajusta orígenes según tu front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Seed Estados de Informe en startup
@app.on_event("startup")
def seed_estados():
    with Session(bind=engine) as db:
        existentes = {e.codigo for e in db.query(EstadoInforme).all()}
        semillas = [
            {"codigo": "borrador", "nombre": "Borrador"},
            {"codigo": "en_revision", "nombre": "En revisión"},
            {"codigo": "final", "nombre": "Final"},
        ]
        cambio = False
        for s in semillas:
            if s["codigo"] not in existentes:
                db.add(EstadoInforme(codigo=s["codigo"], nombre=s["nombre"]))
                cambio = True
        if cambio:
            db.commit()

# Montar routers
app.include_router(pacientes_router)
app.include_router(medicos_router)
app.include_router(estudios_router)
app.include_router(imagenes_router)
app.include_router(informes_router)

@app.get("/_ping")
def ping_root():
    return {"ok": True, "service": "DiagnosticaDoc API"}

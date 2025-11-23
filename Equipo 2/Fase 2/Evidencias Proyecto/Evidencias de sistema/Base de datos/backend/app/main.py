# app/main.py
from pathlib import Path
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from app.routers.ml_router import router as ml_router  # IA
from app.routers.citas_router import router as citas_router
from app.routers.debug_router import router as debug_router

# ==================== ENV & logging ====================

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# ==================== App ====================

app = FastAPI(title="DiagnosticaDoc API", version="1.0.0")

# ==================== CORS (modo bestia para debug) ====================

CORS_ORIGINS = ["*"]  # 🔥 TEMPORAL: todo permitido mientras probamos

logging.info(f"🚀 Iniciando API con CORS_ORIGINS = {CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # pon True solo si usas cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Static / media ====================

MEDIA_DIR = ROOT_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# ==================== Routers ====================

app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(medicos_router)
app.include_router(estudios_router)
app.include_router(imagenes_router)
app.include_router(informes_router, prefix="/informes")
app.include_router(citas_router)
app.include_router(debug_router)
app.include_router(ml_router)  # IA

# ==================== DB & Seed ====================

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def seed_estados():
    with Session(bind=engine) as db:
        existentes = {e.codigo for e in db.query(EstadoInforme).all()}
        semillas = [
            {"codigo": "borrador",    "nombre": "Borrador"},
            {"codigo": "en_revision", "nombre": "En revisión"},
            {"codigo": "final",       "nombre": "Final"},
        ]
        for s in semillas:
            if s["codigo"] not in existentes:
                db.add(EstadoInforme(codigo=s["codigo"], nombre=s["nombre"]))
        db.commit()

# ==================== Utilidades ====================

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

@app.get("/_ping", include_in_schema=False)
def ping_root():
    return {"ok": True, "service": "DiagnosticaDoc API"}

FAVICON_PATH = Path(__file__).resolve().parent / "static" / "favicon.ico"

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    if FAVICON_PATH.exists():
        return FileResponse(str(FAVICON_PATH))
    return JSONResponse(status_code=204, content=None)

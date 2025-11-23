# app/database.py
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from typing import Generator

# ── Carga .env (tolerante a BOM) desde backend/.env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, encoding="utf-8-sig")

# ── Si hay DATABASE_URL explícita en .env, úsala tal cual (ideal para Docker/Cloud)
DATABASE_URL_ENV = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL_ENV:
    # Puede ser: postgresql+psycopg://user:pass@host:5432/dbname
    db_url = DATABASE_URL_ENV
else:
    # Construye desde variables PG*
    PGUSER = (os.getenv("PGUSER") or "postgres").strip()
    PGPASSWORD = (os.getenv("PGPASSWORD") or "").strip()
    PGHOST = (os.getenv("PGHOST") or "localhost").strip()
    PGPORT = int(os.getenv("PGPORT") or "5432")
    PGDATABASE = (os.getenv("PGDATABASE") or "db_diagnosticadoc").strip()

    db_url = URL.create(
        drivername="postgresql+psycopg",
        username=PGUSER,
        password=PGPASSWORD,
        host=PGHOST,
        port=PGPORT,
        database=PGDATABASE,
    )

# ── Conexión
#   - pool_pre_ping evita conexiones colgadas
#   - future=True API moderna
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    future=True,
    # connect_args={"sslmode": "require"}  # <- si tu proveedor exige SSL
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

def get_db() -> Generator:
    """Dependencia FastAPI para sesiones por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_models_create_all():
    """Crea tablas si no usas Alembic. Llama esto al arrancar la app."""
    # IMPORTANTE: importar modelos antes para que Base conozca las clases
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

def test_connection() -> str:
    """Probar conexión (útil en arranque)."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return "DB OK"

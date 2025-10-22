# app/database.py
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL

# Carga .env (tolerante a BOM) desde backend/backend/.env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, encoding="utf-8-sig")

# Lee variables (defaults seguros)
PGUSER = (os.getenv("PGUSER") or "postgres").strip()
PGPASSWORD = (os.getenv("PGPASSWORD") or "pastel123").strip()
PGHOST = (os.getenv("PGHOST") or "localhost").strip()
PGPORT = int(os.getenv("PGPORT") or "5432")
PGDATABASE = (os.getenv("PGDATABASE") or "db_diagnosticadoc").strip()

# Usa el driver de psycopg3
db_url = URL.create(
    drivername="postgresql+psycopg",
    username=PGUSER,
    password=PGPASSWORD,
    host=PGHOST,
    port=PGPORT,
    database=PGDATABASE,
)

# (Opcional) log seguro
print("DB URL (safe) =", db_url.set(password="***"))

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    future=True,
    # connect_args={}  # normalmente no hace falta nada extra
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Usa variable de entorno si está disponible
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Ajusta usuario/clave/host/puerto/db a tu entorno
    "postgresql+psycopg2://postgres:pastel123@localhost:5432/db_diagnosticadoc"
)

# echo=True para ver SQL en consola (útil en desarrollo)
engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

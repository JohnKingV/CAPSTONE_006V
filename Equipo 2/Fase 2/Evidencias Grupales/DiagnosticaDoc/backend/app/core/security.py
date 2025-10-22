# app/core/security.py
import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "pastel123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# Usa pbkdf2_sha256 para evitar problemas de bcrypt (backends nativos y límite 72 bytes)
_pwd = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=29000,  # valor seguro por defecto
)

def hash_password(password: str) -> str:
    return _pwd.hash(password or "")

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain or "", hashed or "")

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

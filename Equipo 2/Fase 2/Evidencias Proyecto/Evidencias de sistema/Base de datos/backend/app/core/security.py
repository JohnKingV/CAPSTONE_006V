# app/core/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

# ========================
# Config
# ========================
# En producción, SOBREESCRIBE SECRET_KEY por variable de entorno segura
SECRET_KEY: str = os.getenv("SECRET_KEY", "pastel123")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# ========================
# Password hashing (pbkdf2_sha256)
# ========================
_pwd = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=29000,  # valor seguro por defecto
)

def hash_password(password: str) -> str:
    """Devuelve el hash seguro de la contraseña."""
    return _pwd.hash(password or "")

def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash."""
    return _pwd.verify(plain or "", hashed or "")

# ========================
# JWT de acceso (login normal)
# ========================
def create_access_token(data: Dict[str, Any], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Crea un JWT de acceso estándar (ej. tras login).
    Incluye 'exp' con vencimiento configurable.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ========================
# Flujo "Establecer contraseña" por link (token con scope)
# ========================
def create_setpwd_token(email: str, ttl_minutes: int = 60) -> str:
    """
    Crea un token de un solo uso para establecer/definir contraseña.
    - sub: email del usuario
    - scope: "set_password"
    - exp: ahora + ttl_minutes
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "scope": "set_password",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def parse_setpwd_token(token: str) -> Optional[str]:
    """
    Valida el token de set-password y retorna el email si es válido.
    Devuelve None si el token es inválido, expiró o el scope no coincide.
    """
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("scope") != "set_password":
            return None
        return data.get("sub")
    except JWTError:
        return None

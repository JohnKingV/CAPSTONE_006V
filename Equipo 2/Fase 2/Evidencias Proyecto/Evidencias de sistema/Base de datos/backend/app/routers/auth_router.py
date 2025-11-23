# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os

from app.database import get_db
from app.models import User, UserRole
from app.schemas import (
    UserCreate,
    Token,
    LoginIn,
    UserOut,
    UserUpdateMe,
    PasswordChange,
    # ↓ esquemas para el flujo set-password
    RequestSetPassword,
    ValidateTokenOut,
    SetPasswordIn,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    # ↓ tokens especiales para set-password
    create_setpwd_token,
    parse_setpwd_token,
)
from app.deps import get_current_user
from app.core.mailer import build_email_set_password, send_email

router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    name="auth_register",
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Normaliza rol (acepta 'Admin', 'Médico', etc.)
    try:
        role_str = payload.role.lower() if isinstance(payload.role, str) else payload.role
        role = UserRole(role_str)  # admin|medico|paciente
    except Exception:
        raise HTTPException(status_code=422, detail="Rol inválido: use admin|medico|paciente")

    # Email único
    if db.query(User).filter(User.email == payload.email.strip().lower()).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear usuario
    user = User(
        email=payload.email.strip().lower(),
        full_name=(payload.full_name or "").strip(),
        password_hash=hash_password(payload.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo registrar (registro duplicado)")
    db.refresh(user)
    return user


# === Login JSON para el frontend ===
@router.post(
    "/login",
    response_model=Token,
    name="auth_login_json",
)
def login_json(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email, "role": user.role.value, "uid": user.id})
    return {"access_token": token, "token_type": "bearer"}


# === OAuth2 Password para Swagger (Authorize) ===
@router.post(
    "/token",
    response_model=Token,
    name="auth_token_password",
)
def login_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # En este flujo, 'username' es el email
    user = db.query(User).filter(User.email == form.username.strip().lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email, "role": user.role.value, "uid": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserOut,
    name="auth_me",
)
def me(user: User = Depends(get_current_user)):
    return user


# === Actualizar perfil del usuario autenticado ===
@router.patch(
    "/me",
    response_model=UserOut,
    name="auth_update_me",
)
def update_me(
    payload: UserUpdateMe,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Si se quiere cambiar email, validar unicidad
    if payload.email and payload.email.strip().lower() != current_user.email:
        exists = db.query(User).filter(User.email == payload.email.strip().lower()).first()
        if exists:
            raise HTTPException(status_code=409, detail="Email ya está en uso")

    # Aplicar cambios si fueron enviados
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
    if payload.nombres is not None:
        current_user.nombres = payload.nombres.strip()
    if payload.apellidos is not None:
        current_user.apellidos = payload.apellidos.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url.strip()
    if payload.email is not None:
        current_user.email = payload.email.strip().lower()

    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos")

    return current_user


# === Cambiar contraseña del usuario autenticado ===
@router.post(
    "/change-password",
    status_code=204,
    name="auth_change_password",
)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no es válida")

    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="La nueva contraseña no puede ser igual a la actual")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return


# =============================================================================
# NUEVO — Flujo "Establecer contraseña" por link (token con scope 'set_password')
# =============================================================================

@router.post(
    "/request-set-password",
    status_code=204,
    name="auth_request_set_password",
)
def request_set_password(payload: RequestSetPassword, db: Session = Depends(get_db)):
    """
    No revela si el email existe: siempre 204.
    Si el usuario existe y está activo, envía un link con token (60 min).
    """
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if user and user.is_active:
        token = create_setpwd_token(user.email, ttl_minutes=60)
        link = f"{FRONTEND_BASE_URL}/set-password?token={token}"
        try:
            msg = build_email_set_password(to_email=user.email, link=link)
            send_email(msg)
        except Exception:
            # No se rompe el flujo por errores de envío
            pass
    return


@router.get(
    "/validate-set-password",
    response_model=ValidateTokenOut,
    name="auth_validate_set_password",
)
def validate_set_password_token(token: str, db: Session = Depends(get_db)):
    """
    Valida el token de set-password. Devuelve email y estado 'valid'.
    """
    email = parse_setpwd_token(token)
    if not email:
        return ValidateTokenOut(email="invalid@example.com", valid=False)
    user = db.query(User).filter(User.email == email).first()
    return ValidateTokenOut(email=email, valid=bool(user and user.is_active))


@router.post(
    "/set-password",
    status_code=204,
    name="auth_set_password",
)
def set_password(body: SetPasswordIn, db: Session = Depends(get_db)):
    """
    Aplica la nueva contraseña si el token es válido.
    """
    email = parse_setpwd_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o inactivo")

    user.password_hash = hash_password(body.new_password)
    db.add(user)
    db.commit()
    return

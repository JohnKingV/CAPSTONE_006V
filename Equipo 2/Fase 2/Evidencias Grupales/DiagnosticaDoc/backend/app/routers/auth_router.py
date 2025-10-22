# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, Token, LoginIn, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


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
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crear usuario
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=role,
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
    user = db.query(User).filter(User.email == data.email).first()
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
    user = db.query(User).filter(User.email == form.username).first()
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

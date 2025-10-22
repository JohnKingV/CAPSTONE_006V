# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, Token, LoginIn, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # 1) normaliza rol (por si llega "Admin"/"Médico")
    try:
        role_str = payload.role.lower() if isinstance(payload.role, str) else payload.role
        role = UserRole(role_str)  # admin|medico|paciente
    except Exception:
        raise HTTPException(status_code=422, detail="Rol inválido: use admin|medico|paciente")

    # 2) email único (evita 500 por constraint)
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # 3) crear usuario
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
        # por si hay otra unique (p.ej. índice concurrente)
        raise HTTPException(status_code=400, detail="No se pudo registrar (registro duplicado)")
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": user.email, "role": user.role.value, "uid": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

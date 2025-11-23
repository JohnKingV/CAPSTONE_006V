# app/routers/medicos_router.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db
from app import models, schemas
from app.core.security import hash_password
from app.models import User, UserRole

router = APIRouter(prefix="/medicos", tags=["Medicos"])


@router.get("/_ping", summary="Ping Medicos")
def ping():
    return {"ok": True}


@router.get(
    "",
    response_model=List[schemas.MedicoOut],
    summary="Listar Medicos",
)
def listar_medicos(db: Session = Depends(get_db)):
    return (
        db.query(models.Medico)
        .order_by(models.Medico.id.desc())
        .all()
    )


@router.post(
    "",
    response_model=schemas.MedicoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Medico",
)
def crear_medico(
    payload: schemas.MedicoCreate,
    db: Session = Depends(get_db),
):
    """
    Crea un médico en la tabla Medico y, si viene email+password,
    crea también un User con rol 'medico' y enlaza medicos.user_id.
    """

    # 1) Preparar datos del médico (sin password ni horarios)
    data_medico = payload.model_dump(exclude={"password", "horarios"})
    hashed_pwd = None

    if payload.password:
        hashed_pwd = hash_password(payload.password)
        data_medico["password_hash"] = hashed_pwd

    # 2) Crear / reutilizar User (rol medico)
    user = None
    if payload.email and payload.password:
        email_norm = payload.email.strip().lower()

        user = db.query(User).filter(User.email == email_norm).first()
        if user:
            # Si ya existe y NO es médico → conflicto
            if user.role != UserRole.medico:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un usuario con este email con otro rol",
                )
            # Si ya es médico, lo reutilizamos tal cual
        else:
            user = User(
                email=email_norm,
                full_name=(payload.nombre or "").strip(),
                password_hash=hashed_pwd or hash_password(payload.password),
                role=UserRole.medico,   # 👈 rol en minúscula, coherente con tu Enum
                is_active=True,
            )
            db.add(user)

    try:
        # Flush para tener user.id si se acaba de crear
        if user:
            db.flush()

        # 3) Crear médico y enlazarlo al user
        med = models.Medico(
            **data_medico,
            user_id=user.id if user else None,
        )
        db.add(med)
        db.flush()  # para obtener med.id

        # 4) Crear horarios si vienen
        if payload.horarios:
            for horario_data in payload.horarios:
                horario = models.HorarioMedico(
                    medico_id=med.id,
                    **horario_data.model_dump(),
                )
                db.add(horario)

        db.commit()

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos (email/registro_colegio duplicado o NOT NULL)",
        ) from e

    db.refresh(med)
    return med


@router.get(
    "/{medico_id}",
    response_model=schemas.MedicoOut,
    summary="Obtener Medico",
)
def obtener_medico(
    medico_id: int,
    db: Session = Depends(get_db),
):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medico no encontrado")
    return med


@router.patch(
    "/{medico_id}",
    response_model=schemas.MedicoOut,
    summary="Actualizar Medico",
)
def actualizar_medico(
    medico_id: int,
    payload: schemas.MedicoUpdate,
    db: Session = Depends(get_db),
):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medico no encontrado")

    # Datos básicos (sin password ni horarios)
    data = payload.model_dump(exclude_unset=True, exclude={"password", "horarios"})
    for k, v in data.items():
        setattr(med, k, v)

    # Actualizar contraseña si se envía
    if payload.password is not None:
        med.password_hash = hash_password(payload.password)

        # Si tiene user asociado y es médico, actualizar también su password
        if med.user_id:
            user = db.get(User, med.user_id)
            if user and user.role == UserRole.medico:
                user.password_hash = med.password_hash
                db.add(user)

    # Actualizar horarios
    if payload.horarios is not None:
        # Borramos todos los horarios anteriores y recreamos
        db.query(models.HorarioMedico).filter(
            models.HorarioMedico.medico_id == med.id
        ).delete()

        for horario_data in payload.horarios:
            horario = models.HorarioMedico(
                medico_id=med.id,
                **horario_data.model_dump(),
            )
            db.add(horario)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos (email/registro_colegio duplicado o NOT NULL)",
        ) from e

    db.refresh(med)
    return med


@router.delete(
    "/{medico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Medico",
)
def eliminar_medico(
    medico_id: int,
    db: Session = Depends(get_db),
):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medico no encontrado")
    db.delete(med)
    db.commit()
    return None

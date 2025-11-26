from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db
from app import models, schemas

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.get("/_ping", summary="Ping Pacientes")
def ping():
    return {"ok": True}

@router.get(
    "",
    response_model=List[schemas.PacienteOut],
    summary="Listar Pacientes",
)
def listar_pacientes(db: Session = Depends(get_db)):
    return (
        db.query(models.Paciente)
        .order_by(models.Paciente.id.desc())
        .all()
    )

@router.post(
    "",
    response_model=schemas.PacienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Paciente",
)
def crear_paciente(
    payload: schemas.PacienteCreate,
    db: Session = Depends(get_db),
):
    pac = models.Paciente(**payload.model_dump())
    db.add(pac)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos (documento/email duplicado o NOT NULL)",
        ) from e
    db.refresh(pac)
    return pac

@router.get(
    "/{paciente_id}",
    response_model=schemas.PacienteOut,
    summary="Obtener Paciente",
)
def obtener_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
):
    pac = db.get(models.Paciente, paciente_id)
    if not pac:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return pac

@router.patch(
    "/{paciente_id}",
    response_model=schemas.PacienteOut,
    summary="Actualizar Paciente",
)
def actualizar_paciente(
    paciente_id: int,
    payload: schemas.PacienteUpdate,
    db: Session = Depends(get_db),
):
    pac = db.get(models.Paciente, paciente_id)
    if not pac:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(pac, campo, valor)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de datos (documento/email duplicado o NOT NULL)",
        ) from e
    db.refresh(pac)
    return pac

@router.delete(
    "/{paciente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Paciente",
)
def eliminar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
):
    pac = db.get(models.Paciente, paciente_id)
    if not pac:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    db.delete(pac)
    db.commit()
    return None

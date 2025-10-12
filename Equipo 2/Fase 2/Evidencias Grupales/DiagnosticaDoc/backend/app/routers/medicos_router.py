from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.get("/_ping", summary="Ping Médicos")
def ping():
    return {"ok": True}

@router.get("", response_model=List[schemas.MedicoOut], summary="Listar Médicos")
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).order_by(models.Medico.id.desc()).all()

@router.post("", response_model=schemas.MedicoOut, status_code=status.HTTP_201_CREATED, summary="Crear Médico")
def crear_medico(payload: schemas.MedicoCreate, db: Session = Depends(get_db)):
    med = models.Medico(**payload.model_dump())
    db.add(med)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (email/registro_colegio duplicado o NOT NULL)") from e
    db.refresh(med)
    return med

@router.get("/{medico_id}", response_model=schemas.MedicoOut, summary="Obtener Médico")
def obtener_medico(medico_id: int, db: Session = Depends(get_db)):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return med

@router.patch("/{medico_id}", response_model=schemas.MedicoOut, summary="Actualizar Médico")
def actualizar_medico(medico_id: int, payload: schemas.MedicoUpdate, db: Session = Depends(get_db)):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(med, k, v)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (email/registro_colegio duplicado o NOT NULL)") from e
    db.refresh(med)
    return med

@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Médico")
def eliminar_medico(medico_id: int, db: Session = Depends(get_db)):
    med = db.get(models.Medico, medico_id)
    if not med:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    db.delete(med)
    db.commit()
    return None

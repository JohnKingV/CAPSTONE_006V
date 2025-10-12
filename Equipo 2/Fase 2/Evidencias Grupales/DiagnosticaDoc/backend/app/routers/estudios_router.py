from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/estudios", tags=["Estudios"])

@router.get("/_ping", summary="Ping Estudios")
def ping():
    return {"ok": True}

@router.get("", response_model=List[schemas.EstudioOut], summary="Listar Estudios")
def listar_estudios(db: Session = Depends(get_db)):
    return db.query(models.Estudio).order_by(models.Estudio.id.desc()).all()

@router.post("", response_model=schemas.EstudioOut, status_code=status.HTTP_201_CREATED, summary="Crear Estudio")
def crear_estudio(payload: schemas.EstudioCreate, db: Session = Depends(get_db)):
    if not db.get(models.Paciente, payload.paciente_id):
        raise HTTPException(status_code=400, detail="paciente_id no existe")
    if payload.medico_id and not db.get(models.Medico, payload.medico_id):
        raise HTTPException(status_code=400, detail="medico_id no existe")

    est = models.Estudio(**payload.model_dump())
    db.add(est)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (FK/unicidad/NOT NULL)") from e
    db.refresh(est)
    return est

@router.get("/{estudio_id}", response_model=schemas.EstudioOut, summary="Obtener Estudio")
def obtener_estudio(estudio_id: int, db: Session = Depends(get_db)):
    est = db.get(models.Estudio, estudio_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    return est

@router.patch("/{estudio_id}", response_model=schemas.EstudioOut, summary="Actualizar Estudio")
def actualizar_estudio(estudio_id: int, payload: schemas.EstudioUpdate, db: Session = Depends(get_db)):
    est = db.get(models.Estudio, estudio_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    cambios = payload.model_dump(exclude_unset=True)
    if "paciente_id" in cambios and cambios["paciente_id"]:
        if not db.get(models.Paciente, cambios["paciente_id"]):
            raise HTTPException(status_code=400, detail="paciente_id no existe")
    if "medico_id" in cambios and cambios["medico_id"]:
        if not db.get(models.Medico, cambios["medico_id"]):
            raise HTTPException(status_code=400, detail="medico_id no existe")

    for k, v in cambios.items():
        setattr(est, k, v)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (FK/unicidad/NOT NULL)") from e
    db.refresh(est)
    return est

@router.delete("/{estudio_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Estudio")
def eliminar_estudio(estudio_id: int, db: Session = Depends(get_db)):
    est = db.get(models.Estudio, estudio_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    db.delete(est)
    db.commit()
    return None

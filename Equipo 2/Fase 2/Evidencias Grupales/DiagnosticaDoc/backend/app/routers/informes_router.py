from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db
from app import models, schemas

router = APIRouter(prefix="/informes", tags=["Informes"])

@router.get("/_ping", summary="Ping Informes")
def ping():
    return {"ok": True}

@router.get("", response_model=List[schemas.InformeOut], summary="Listar Informes")
def listar_informes(db: Session = Depends(get_db)):
    return db.query(models.Informe).order_by(models.Informe.id.desc()).all()

@router.post("", response_model=schemas.InformeOut, status_code=status.HTTP_201_CREATED, summary="Crear Informe")
def crear_informe(payload: schemas.InformeCreate, db: Session = Depends(get_db)):
    if not db.get(models.Estudio, payload.estudio_id):
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    if payload.estado_id is not None and not db.get(models.EstadoInforme, payload.estado_id):
        raise HTTPException(status_code=404, detail="Estado de informe no encontrado")

    inf = models.Informe(**payload.model_dump())
    db.add(inf)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (NOT NULL/FK)") from e
    db.refresh(inf)
    return inf

@router.get("/{informe_id}", response_model=schemas.InformeOut, summary="Obtener Informe")
def obtener_informe(informe_id: int, db: Session = Depends(get_db)):
    inf = db.get(models.Informe, informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return inf

@router.patch("/{informe_id}", response_model=schemas.InformeOut, summary="Actualizar Informe")
def actualizar_informe(informe_id: int, payload: schemas.InformeUpdate, db: Session = Depends(get_db)):
    inf = db.get(models.Informe, informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")

    cambios = payload.model_dump(exclude_unset=True)
    if "estado_id" in cambios and cambios["estado_id"] is not None:
        if not db.get(models.EstadoInforme, cambios["estado_id"]):
            raise HTTPException(status_code=404, detail="Estado de informe no encontrado")

    for k, v in cambios.items():
        setattr(inf, k, v)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (NOT NULL/FK)") from e
    db.refresh(inf)
    return inf

@router.delete("/{informe_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Informe")
def eliminar_informe(informe_id: int, db: Session = Depends(get_db)):
    inf = db.get(models.Informe, informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    db.delete(inf)
    db.commit()
    return None

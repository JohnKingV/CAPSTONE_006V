# app/routers/informes_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database import get_db
from app.models import Informe, EstadoInforme, Estudio
from app.schemas import InformeCreate, InformeOut, InformeUpdate  # ajusta si tus nombres difieren

router = APIRouter(tags=["Informes"])

def get_estado_borrador_id(db: Session) -> int:
    obj = db.query(EstadoInforme).filter(EstadoInforme.codigo == "borrador").first()
    if not obj:
        raise HTTPException(status_code=500, detail="No existe estado 'borrador'")
    return obj.id

@router.get("", response_model=List[InformeOut])
def list_informes(db: Session = Depends(get_db)):
    return db.query(Informe).all()

@router.get("/{informe_id}", response_model=InformeOut)
def get_informe(informe_id: int, db: Session = Depends(get_db)):
    inf = db.query(Informe).get(informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    return inf

@router.post("", response_model=InformeOut, status_code=201)
def create_informe(payload: InformeCreate, db: Session = Depends(get_db)):
    # valida estudio
    estudio = db.query(Estudio).get(payload.estudio_id)
    if not estudio:
        raise HTTPException(status_code=404, detail="Estudio no existe")

    # default estado -> 'borrador' si no llega
    estado_id = payload.estado_id or get_estado_borrador_id(db)

    # evita duplicado por UNIQUE(estudio_id)
    ya = db.query(Informe).filter(Informe.estudio_id == payload.estudio_id).first()
    if ya:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este estudio ya tiene un informe. Usa PATCH para actualizar."
        )

    inf = Informe(
        estudio_id=payload.estudio_id,
        estado_id=estado_id,
        contenido=payload.contenido,
        observaciones=payload.observaciones,
    )
    try:
        db.add(inf)
        db.commit()
        db.refresh(inf)
        return inf
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se pudo crear el informe (constraint).")

@router.patch("/{informe_id}", response_model=InformeOut)
def update_informe(informe_id: int, payload: InformeUpdate, db: Session = Depends(get_db)):
    inf = db.query(Informe).get(informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")

    if payload.contenido is not None:
        inf.contenido = payload.contenido
    if payload.observaciones is not None:
        inf.observaciones = payload.observaciones
    if payload.estado_id is not None:
        inf.estado_id = payload.estado_id

    db.commit()
    db.refresh(inf)
    return inf

@router.delete("/{informe_id}", status_code=204)
def delete_informe(informe_id: int, db: Session = Depends(get_db)):
    inf = db.query(Informe).get(informe_id)
    if not inf:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    db.delete(inf)
    db.commit()

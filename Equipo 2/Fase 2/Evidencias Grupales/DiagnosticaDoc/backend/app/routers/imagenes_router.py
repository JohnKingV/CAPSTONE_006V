from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/imagenes", tags=["Imágenes"])

def _get_estudio_or_400(db: Session, estudio_id: int) -> models.Estudio:
    est = db.get(models.Estudio, estudio_id)
    if not est:
        raise HTTPException(status_code=400, detail="estudio_id inválido: no existe el estudio")
    return est

@router.post("", response_model=schemas.ImagenOut, status_code=status.HTTP_201_CREATED, summary="Crear Imagen")
def crear_imagen(payload: schemas.ImagenCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    _get_estudio_or_400(db, data["estudio_id"])

    img = models.Imagen(**data)
    db.add(img)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (unicidad/NOT NULL/FK)") from e
    db.refresh(img)
    return img

@router.get("", response_model=List[schemas.ImagenOut], summary="Listar Imágenes")
def listar_imagenes(
    db: Session = Depends(get_db),
    estudio_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = db.query(models.Imagen)
    if estudio_id is not None:
        q = q.filter(models.Imagen.estudio_id == estudio_id)
    return q.order_by(models.Imagen.id.desc()).offset(offset).limit(limit).all()

@router.get("/{imagen_id}", response_model=schemas.ImagenOut, summary="Obtener Imagen")
def obtener_imagen(imagen_id: int, db: Session = Depends(get_db)):
    img = db.get(models.Imagen, imagen_id)
    if not img:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return img

@router.patch("/{imagen_id}", response_model=schemas.ImagenOut, summary="Actualizar Imagen")
def actualizar_imagen(imagen_id: int, payload: schemas.ImagenUpdate, db: Session = Depends(get_db)):
    img = db.get(models.Imagen, imagen_id)
    if not img:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    cambios = payload.model_dump(exclude_unset=True)
    if "estudio_id" in cambios and cambios["estudio_id"]:
        _get_estudio_or_400(db, cambios["estudio_id"])

    for k, v in cambios.items():
        setattr(img, k, v)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto de datos (unicidad/NOT NULL/FK)") from e
    db.refresh(img)
    return img

@router.delete("/{imagen_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Imagen")
def eliminar_imagen(imagen_id: int, db: Session = Depends(get_db)):
    img = db.get(models.Imagen, imagen_id)
    if not img:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    db.delete(img)
    db.commit()
    return None

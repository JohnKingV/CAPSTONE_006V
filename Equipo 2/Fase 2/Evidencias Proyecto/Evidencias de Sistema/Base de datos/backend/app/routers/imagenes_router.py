# app/routers/imagenes_router.py
from pathlib import Path
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/imagenes", tags=["Imagenes"])

# Carpeta donde se guardarán los archivos
UPLOAD_DIR = Path("media/imagenes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _get_estudio_or_400(db: Session, estudio_id: int) -> models.Estudio:
    estudio = db.query(models.Estudio).filter(models.Estudio.id == estudio_id).first()
    if not estudio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estudio {estudio_id} no existe",
        )
    return estudio


def _get_imagen_or_404(db: Session, imagen_id: int) -> models.Imagen:
    img = db.query(models.Imagen).filter(models.Imagen.id == imagen_id).first()
    if not img:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imagen {imagen_id} no encontrada",
        )
    return img


# ============================================
# ENDPOINTS JSON
# ============================================

@router.get("", response_model=List[schemas.ImagenOut])
def listar_imagenes(db: Session = Depends(get_db)):
    """
    Devuelve la lista simple de imágenes (array de ImagenOut).
    El frontend ya adapta esto a { items, total }.
    """
    imgs = db.query(models.Imagen).order_by(models.Imagen.id.desc()).all()
    return imgs


@router.post("", response_model=schemas.ImagenOut, status_code=status.HTTP_201_CREATED)
def crear_imagen(payload: schemas.ImagenCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    _get_estudio_or_400(db, data["estudio_id"])

    img = models.Imagen(**data)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.patch(
    "/{imagen_id}",
    response_model=schemas.ImagenOut,
    status_code=status.HTTP_200_OK,
)
def actualizar_imagen(
    imagen_id: int,
    payload: schemas.ImagenUpdate,
    db: Session = Depends(get_db),
):
    img = _get_imagen_or_404(db, imagen_id)

    data = payload.model_dump(exclude_unset=True)
    if "estudio_id" in data:
        _get_estudio_or_400(db, data["estudio_id"])

    for k, v in data.items():
        setattr(img, k, v)

    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.delete(
    "/{imagen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_imagen(imagen_id: int, db: Session = Depends(get_db)):
    img = _get_imagen_or_404(db, imagen_id)
    db.delete(img)
    db.commit()
    return None


# ============================================
# NUEVOS ENDPOINTS MULTIPART (archivo real)
# ============================================

@router.post(
    "/upload",
    response_model=schemas.ImagenOut,
    status_code=status.HTTP_201_CREATED,
)
async def subir_imagen(
    estudio_id: int = Form(...),
    file: UploadFile = File(...),
    filename: str | None = Form(None),
    mimetype: str | None = Form(None),
    size_bytes: int | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Crea una imagen NUEVA recibiendo un archivo real (multipart/form-data).
    Campos esperados en el FormData:
      - estudio_id (int)
      - file (UploadFile)
      - filename? (opcional)
      - mimetype? (opcional)
      - size_bytes? (opcional)
    """
    _get_estudio_or_400(db, estudio_id)

    original_name = filename or file.filename or "archivo"
    ext = Path(original_name).suffix or ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    out_path = UPLOAD_DIR / unique_name

    content = await file.read()
    out_path.write_bytes(content)

    img = models.Imagen(
        estudio_id=estudio_id,
        filename=original_name,
        url=f"/media/imagenes/{unique_name}",
        mimetype=mimetype or file.content_type,
        size_bytes=size_bytes or len(content),
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.patch(
    "/{imagen_id}/upload",
    response_model=schemas.ImagenOut,
    status_code=status.HTTP_200_OK,
)
async def actualizar_imagen_con_archivo(
    imagen_id: int,
    file: UploadFile = File(...),
    filename: str | None = Form(None),
    mimetype: str | None = Form(None),
    size_bytes: int | None = Form(None),
    estudio_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Actualiza el archivo asociado a una imagen existente.
    Permite opcionalmente cambiar:
      - estudio_id
      - filename, mimetype, size_bytes
    """
    img = _get_imagen_or_404(db, imagen_id)

    if estudio_id is not None:
        _get_estudio_or_400(db, estudio_id)
        img.estudio_id = estudio_id

    original_name = filename or file.filename or img.filename or "archivo"
    ext = Path(original_name).suffix or ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    out_path = UPLOAD_DIR / unique_name

    content = await file.read()
    out_path.write_bytes(content)

    img.filename = original_name
    img.url = f"/media/imagenes/{unique_name}"
    img.mimetype = mimetype or file.content_type
    img.size_bytes = size_bytes or len(content)

    db.add(img)
    db.commit()
    db.refresh(img)
    return img

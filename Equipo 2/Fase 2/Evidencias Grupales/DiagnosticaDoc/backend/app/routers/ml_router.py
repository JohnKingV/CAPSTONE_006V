from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import os, io, logging
import numpy as np
from PIL import Image, ImageFile
from typing import Optional

# Evita errores por imágenes truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Usa tf.keras (no keras a secas)
from tensorflow.keras.models import load_model

router = APIRouter(prefix="", tags=["IA Médica"])

# === Config ===
MODEL_PATH = os.getenv("TB_MODEL_PATH", "app/ml/model_tb.keras")
IA_MOCK = os.getenv("IA_MOCK", "0") == "1"
LABELS = ["normal", "tuberculosis"]
IMG_SIZE = (224, 224)   # si tu modelo usa otro tamaño, cámbialo o infiérelo

log = logging.getLogger("ml")
if not log.handlers:
    logging.basicConfig(level=logging.INFO)

_model = None
_model_error = None

def _load_model_once():
    global _model, _model_error
    if _model is not None or _model_error is not None:
        return
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modelo no encontrado en {os.path.abspath(MODEL_PATH)}")
        _model = load_model(MODEL_PATH)
        log.info(f"[ML] Modelo cargado: {os.path.abspath(MODEL_PATH)}")
    except Exception as e:
        _model_error = e
        log.error(f"[ML] Error cargando modelo: {e}")

def _read_image(b: bytes) -> np.ndarray:
    try:
        im = Image.open(io.BytesIO(b)).convert("RGB").resize(IMG_SIZE)
        arr = np.asarray(im, dtype="float32") / 255.0
        return arr
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Imagen inválida: {e}")

def _predict_array(arr: np.ndarray):
    if IA_MOCK:
        # simulación para probar pipeline si aún no tienes el modelo
        return {"normal": 0.85, "tuberculosis": 0.15}

    _load_model_once()
    if _model_error is not None:
        raise HTTPException(status_code=500, detail=f"No se pudo cargar el modelo: {_model_error}")
    if _model is None:
        raise HTTPException(status_code=500, detail="Modelo no inicializado")

    try:
        batch = np.expand_dims(arr, axis=0)
        preds = _model.predict(batch)[0]
        preds = np.clip(preds, 0.0, 1.0)
        s = float(np.sum(preds)) or 1.0
        preds = preds / s  # normaliza por si vinieron logits
        return {"normal": float(preds[0]), "tuberculosis": float(preds[1])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir: {e}")

def _json_out(result: dict):
    return JSONResponse({
        "normal": result["normal"],
        "tuberculosis": result["tuberculosis"],
        "predictions": [
            {"label": "Normal", "score": result["normal"]},
            {"label": "Tuberculosis", "score": result["tuberculosis"]},
        ],
    })

@router.get("/_ping")
def ping():
    try:
        _load_model_once()
        ok = _model is not None
        err = str(_model_error) if _model_error else None
    except Exception as e:
        ok, err = False, str(e)
    return {
        "ok": True,
        "model_loaded": ok,
        "model_path": os.path.abspath(MODEL_PATH),
        "mock": IA_MOCK,
        "error": err,
    }

# =========
# 1) /predict → con UploadFile (Swagger muestra inputs 'file' e 'image')
#    IMPORTANTE: en /docs NO marques "Send empty value" en 'image'
# =========
@router.post("/predict", summary="Analizar RX (con campos visibles en Swagger)")
async def predict_with_uploads(
    file: Optional[UploadFile] = File(default=None),
    image: Optional[UploadFile] = File(default=None)
):
    up = file or image
    if up is None:
        raise HTTPException(status_code=422, detail="Sube la imagen en 'file' (o 'image') como archivo")
    data = await up.read()
    if not data:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    arr = _read_image(data)
    result = _predict_array(arr)
    return _json_out(result)

# =========
# 2) /predict_flex → robusto: lee el form y IGNORA campos vacíos
#    Úsalo si en Swagger marcan 'Send empty value' o para front/curl
# =========
@router.post("/predict_flex", summary="Analizar RX (tolerante a formularios vacíos)")
async def predict_flex(request: Request):
    form = await request.form()
    up = form.get("file") or form.get("image")
    if not isinstance(up, UploadFile):
        raise HTTPException(status_code=422, detail="Sube la imagen en 'file' (o 'image') como archivo")
    data = await up.read()
    if not data:
        raise HTTPException(status_code=400, detail="Archivo vacío")
    arr = _read_image(data)
    result = _predict_array(arr)
    return _json_out(result)

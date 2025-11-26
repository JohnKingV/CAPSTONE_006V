#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
infer_one_tb.py
Inferencia para una sola imagen con model_tb.keras
- Lee model_tb_meta.json para clases e input_shape.
- Normaliza como en training (Rescaling 1/255).
- Umbral opcional para binario.
"""

import os
import json
import argparse
import numpy as np
from PIL import Image
import tensorflow as tf

def load_meta(meta_path="model_tb_meta.json"):
    meta = {
        "input_shape": (224, 224, 3),
        "class_names": ["Normal", "Tuberculosis"],
        "arch": "light"
    }
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            try:
                meta.update(json.load(f))
            except Exception:
                pass
    # Asegura tipos correctos
    ishape = meta.get("input_shape", [224,224,3])
    if isinstance(ishape, (list, tuple)) and len(ishape) == 3:
        meta["input_shape"] = tuple(int(x) for x in ishape)
    else:
        meta["input_shape"] = (224,224,3)
    classes = meta.get("class_names", ["Normal","Tuberculosis"])
    meta["class_names"] = list(classes)
    return meta

def load_image(path, target_size):
    """Carga imagen, fuerza RGB, resize, normaliza [0,1]."""
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize(target_size, Image.BILINEAR)
    arr = np.asarray(img, dtype="float32") / 255.0
    return np.expand_dims(arr, axis=0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="app/ml/model_tb.keras", help="Ruta al modelo .keras")
    parser.add_argument("--image", type=str, required=True, help="Ruta a la imagen a inferir")
    parser.add_argument("--meta", type=str, default="model_tb_meta.json", help="Ruta a meta JSON")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Umbral para binario: prob(clase positiva) >= threshold => positiva")
    parser.add_argument("--json", action="store_true", help="Imprime sólo JSON")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        raise FileNotFoundError(f"Modelo no encontrado: {args.model}")

    meta = load_meta(args.meta)
    class_names = meta["class_names"]
    H, W, C = meta["input_shape"]
    target_size = (W, H) if isinstance(W, int) else (224, 224)

    # Carga modelo
    model = tf.keras.models.load_model(args.model, compile=False)

    # Prepara batch
    batch = load_image(args.image, target_size)
    probs = model.predict(batch, verbose=0)[0]

    # Clip/normalize por seguridad numérica
    probs = np.clip(probs, 0.0, 1.0)
    s = float(np.sum(probs))
    probs = probs / (s if s > 0 else 1.0)

    # Post-procesamiento
    result = {
        "classes": class_names,
        "probs": {class_names[i]: float(probs[i]) for i in range(len(class_names))}
    }

    # Decisión binaria opcional (si exactamente 2 clases)
    if len(class_names) == 2 and args.threshold is not None:
        pos_idx = 1  # por convención: índice 1 = "Tuberculosis"
        pred_pos = probs[pos_idx] >= float(args.threshold)
        result["threshold"] = float(args.threshold)
        result["prediction"] = class_names[pos_idx] if pred_pos else class_names[1 - pos_idx]
    else:
        # Multi-clase o sin threshold: argmax
        result["prediction"] = class_names[int(np.argmax(probs))]

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"\nModelo: {os.path.abspath(args.model)}")
        print(f"Meta:   {os.path.abspath(args.meta)}")
        print(f"Imagen: {os.path.abspath(args.image)}")
        print("Clases:", class_names)
        for k, v in result["probs"].items():
            print(f"  - {k:12s}: {v:0.4f}")
        if "threshold" in result:
            print(f"Umbral : {result['threshold']}")
        print("Predicción:", result["prediction"], "\n")

if __name__ == "__main__":
    main()

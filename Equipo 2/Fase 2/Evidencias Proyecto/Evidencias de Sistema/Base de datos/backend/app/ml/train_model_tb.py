#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
train_model_tb.py
Entrena un modelo CNN (TensorFlow/Keras) para RX de tórax (Normal vs Tuberculosis)
y exporta `model_tb.keras` listo para tu backend FastAPI.

Requisitos:
    pip install "tensorflow==2.15.0" "numpy==1.26.4" "pillow==10.4.0" scikit-learn matplotlib
"""

import os
import argparse
import json
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers as L, models as M
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
)
from sklearn.metrics import classification_report, confusion_matrix
import itertools
import matplotlib.pyplot as plt

AUTOTUNE = tf.data.AUTOTUNE


# ---------------------------------------------------------------------
# Utilidades básicas
# ---------------------------------------------------------------------
def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


# ---------------------------------------------------------------------
# Modelo CNN simple
# ---------------------------------------------------------------------
def build_model(input_shape=(224, 224, 3), num_classes=2, dropout=0.5):
    inputs = L.Input(shape=input_shape)
    x = inputs

    # Bloque 1
    x = L.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = L.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = L.MaxPool2D()(x)
    x = L.BatchNormalization()(x)

    # Bloque 2
    x = L.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = L.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = L.MaxPool2D()(x)
    x = L.BatchNormalization()(x)

    # Bloque 3
    x = L.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = L.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = L.MaxPool2D()(x)
    x = L.BatchNormalization()(x)

    x = L.GlobalAveragePooling2D()(x)
    x = L.Dropout(dropout)(x)
    x = L.Dense(128, activation="relu")(x)
    x = L.Dropout(dropout)(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)

    model = M.Model(inputs, outputs, name="tb_cnn_light")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(name="acc"),
            tf.keras.metrics.AUC(name="auc", multi_label=True)
        ]
    )
    return model


# ---------------------------------------------------------------------
# EfficientNet (opcional)
# ---------------------------------------------------------------------
def build_efficientnet(input_shape=(224,224,3), num_classes=2, base="B0", dropout=0.4):
    from tensorflow.keras.applications import EfficientNetB0, EfficientNetB1, EfficientNetB2
    base_map = {"B0": EfficientNetB0, "B1": EfficientNetB1, "B2": EfficientNetB2}
    Base = base_map.get(base, EfficientNetB0)
    backbone = Base(include_top=False, weights="imagenet", input_shape=input_shape, pooling="avg")

    inputs = L.Input(shape=input_shape)
    x = backbone(inputs, training=False)
    x = L.Dropout(dropout)(x)
    outputs = L.Dense(num_classes, activation="softmax")(x)

    model = M.Model(inputs, outputs, name=f"tb_efficientnet_{base.lower()}")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(name="acc"),
            tf.keras.metrics.AUC(name="auc", multi_label=True)
        ]
    )
    return model


# ---------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------
def make_datasets(data_dir, img_size=(224,224), batch_size=32, val_split=0.2,
                  use_dirs=True, class_names=("Normal","Tuberculosis")):

    if use_dirs:
        train_dir = os.path.join(data_dir, "train")
        val_dir   = os.path.join(data_dir, "val")
        if not (os.path.isdir(train_dir) and os.path.isdir(val_dir)):
            raise FileNotFoundError("Faltan subdirectorios DATA_DIR/train y DATA_DIR/val con clases dentro.")

        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir, labels="inferred", label_mode="categorical",
            class_names=list(class_names), image_size=img_size, batch_size=batch_size, shuffle=True
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            val_dir, labels="inferred", label_mode="categorical",
            class_names=list(class_names), image_size=img_size, batch_size=batch_size, shuffle=False
        )
    else:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, labels="inferred", label_mode="categorical",
            validation_split=val_split, subset="training", seed=42,
            class_names=list(class_names), image_size=img_size, batch_size=batch_size, shuffle=True
        )
        val_ds = tf.keras.utils.image_dataset_from_directory(
            data_dir, labels="inferred", label_mode="categorical",
            validation_split=val_split, subset="validation", seed=42,
            class_names=list(class_names), image_size=img_size, batch_size=batch_size, shuffle=False
        )

    # Normalización + augment
    norm = L.Rescaling(1./255)
    aug = tf.keras.Sequential([
        L.RandomFlip("horizontal"),
        L.RandomRotation(0.05),
        L.RandomZoom(0.05),
        L.RandomTranslation(0.05, 0.05),
    ], name="augment")

    def map_train(x, y):
        return norm(aug(x, training=True)), y

    def map_val(x, y):
        return norm(x), y

    train_ds = train_ds.map(map_train, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    val_ds   = val_ds.map(map_val,   num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    return train_ds, val_ds


# ---------------------------------------------------------------------
# Matriz de confusión
# ---------------------------------------------------------------------
def plot_confusion(cm, classes, normalize=True, title='Matriz de confusión'):
    if normalize:
        cm = cm.astype('float') / (cm.sum(axis=1, keepdims=True) + 1e-9)
    plt.figure(figsize=(5,4))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 ha="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.ylabel('Etiqueta real')
    plt.xlabel('Predicción')
    plt.tight_layout()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--use-dirs", action="store_true")
    parser.add_argument("--arch", choices=["light","effb0","effb1","effb2"], default="light")
    parser.add_argument("--out", type=str, default="app/ml/model_tb.keras")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    seed_everything(args.seed)
    img_shape = (args.img_size, args.img_size, 3)
    class_names = ("Normal","Tuberculosis")

    print(f"[INFO] Clases: {class_names}")
    print("[INFO] Creando datasets...")
    train_ds, val_ds = make_datasets(
        args.data, (args.img_size, args.img_size),
        args.batch_size, args.val_split, args.use_dirs, class_names
    )

    print(f"[INFO] Construyendo modelo ({args.arch})...")
    if args.arch == "light":
        model = build_model(img_shape, num_classes=2)
    else:
        eff_map = {"effb0":"B0","effb1":"B1","effb2":"B2"}
        model = build_efficientnet(img_shape, num_classes=2, base=eff_map[args.arch])
    model.summary()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    ckp = ModelCheckpoint(args.out, monitor="val_auc", mode="max", save_best_only=True, verbose=1)
    early = EarlyStopping(monitor="val_auc", mode="max", patience=8, restore_best_weights=True, verbose=1)
    redlr = ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=4, min_lr=1e-7, verbose=1)
    csv = CSVLogger("train_tb_log.csv", append=False)

    print("[INFO] Entrenando...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=[ckp, early, redlr, csv]
    )

    print(f"[OK] Mejor modelo guardado en: {os.path.abspath(args.out)}")

    # Evaluación
    print("[INFO] Evaluando en validación...")
    y_true, y_pred = [], []
    for xb, yb in val_ds:
        probs = model.predict(xb, verbose=0)
        yp = np.argmax(probs, axis=1)
        y_true.extend(np.argmax(yb.numpy(), axis=1))  # one-hot → índice
        y_pred.extend(yp.tolist())

    print(classification_report(y_true, y_pred, target_names=list(class_names)))
    cm = confusion_matrix(y_true, y_pred)
    plot_confusion(cm, list(class_names), normalize=True)
    plt.savefig("confusion_matrix_val.png", dpi=140)
    print("[OK] confusion_matrix_val.png guardado.")

    # Metadata
    meta = {
        "input_shape": img_shape,
        "class_names": list(class_names),
        "arch": args.arch,
        "epochs_trained": len(history.history.get("loss", []))
    }
    with open("model_tb_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("[OK] model_tb_meta.json guardado.")


if __name__ == "__main__":
    main()

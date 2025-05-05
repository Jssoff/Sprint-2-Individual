import os
import numpy as np
import nibabel as nib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, MaxPooling3D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from .models import ImagenMedica

def load_and_preprocess_data_from_db():
    """
    Carga y preprocesa las imágenes MRI y sus etiquetas desde la base de datos.
    """
    images = []
    labels = []

    # Obtener todas las imágenes de la base de datos
    imagenes = ImagenMedica.objects.all()

    for imagen in imagenes:
        try:
            # Cargar la imagen desde el archivo asociado
            img = nib.load(imagen.archivo.path).get_fdata()
            img = np.expand_dims(img, axis=-1)  # Añadir canal para imágenes 3D
            images.append(img)

            # Etiqueta: 1 si es epilepsia, 0 si no lo es (basado en un campo booleano o similar)
            labels.append(1 if imagen.nombre.lower().startswith('epilepsia') else 0)
        except Exception as e:
            print(f"Error al cargar la imagen {imagen.archivo.path}: {e}")

    images = np.array(images, dtype=np.float32)
    labels = np.array(labels, dtype=np.int32)

    # Normalizar las imágenes
    images = (images - np.min(images)) / (np.max(images) - np.min(images))

    return images, labels

def build_cnn_model(input_shape):
    """
    Construye y compila un modelo CNN para clasificación de imágenes 3D.
    """
    model = Sequential([
        Conv3D(32, kernel_size=(3, 3, 3), activation='relu', input_shape=input_shape),
        MaxPooling3D(pool_size=(2, 2, 2)),
        Dropout(0.3),

        Conv3D(64, kernel_size=(3, 3, 3), activation='relu'),
        MaxPooling3D(pool_size=(2, 2, 2)),
        Dropout(0.3),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.4),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model

def train_model(data_dir, model_save_path):
    """
    Entrena el modelo CNN con los datos proporcionados.
    """
    # Cargar y preprocesar los datos
    images, labels = load_and_preprocess_data_from_db()

    # Dividir los datos en conjuntos de entrenamiento y validación
    X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

    # Construir el modelo
    model = build_cnn_model(input_shape=X_train.shape[1:])

    # Entrenar el modelo
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=8)

    # Guardar el modelo entrenado
    model.save(model_save_path)
    print(f"Modelo guardado en {model_save_path}")
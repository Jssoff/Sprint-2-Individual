from django.shortcuts import render, get_object_or_404
from imagen.models import ImagenMedica
from pacientes.models import Paciente


import nibabel as nib
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import plotly.graph_objects as go
from nilearn import plotting, image
from nilearn.image import resample_img
import warnings
import logging

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def visualizar_imagenes_paciente(request, paciente_id):
    # Obtener el paciente desde la base de datos
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Recuperar todas las imágenes asociadas al paciente
    imagenes = ImagenMedica.objects.filter(paciente=paciente).order_by('-fecha_carga')

    # Crear una lista de visualizaciones con las rutas de las imágenes PNG
    visualizaciones = []
    for imagen in imagenes:
        if imagen.archivo.name.endswith('.png'):
            visualizaciones.append({
                'nombre': imagen.nombre,
                'ruta': imagen.archivo.url  # Usar la URL del archivo para mostrarlo en el HTML
            })

        # Agregar vistas adicionales si existen
        base_name = os.path.splitext(imagen.archivo.name)[0]
        for view in ['_axial.png', '_sagittal.png', '_coronal.png']:
            view_path = os.path.join(settings.MEDIA_URL, f"{base_name}{view}")
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, f"{base_name}{view}")):
                visualizaciones.append({
                    'nombre': f"{imagen.nombre} {view.split('_')[1].split('.')[0].capitalize()}",
                    'ruta': view_path
                })

        # Agregar las rutas de las vistas sagital y coronal al contexto
        if imagen.vista_sagital:
            visualizaciones.append({
                'nombre': f"{imagen.nombre} Sagital",
                'ruta': imagen.vista_sagital.url
            })
        if imagen.vista_coronal:
            visualizaciones.append({
                'nombre': f"{imagen.nombre} Coronal",
                'ruta': imagen.vista_coronal.url
            })

    return render(request, 'diagnostico/visualizar_imagenes_paciente.html', {
        'paciente': paciente,
        'visualizaciones': visualizaciones
    })

def visualizar_imagen(request, imagen_id):
    logger.debug("Iniciando la visualización de la imagen con ID: %s", imagen_id)

    # Obtener la imagen desde la base de datos
    imagen = get_object_or_404(ImagenMedica, id=imagen_id)
    nifti_path = imagen.archivo.path
    logger.debug("Ruta del archivo NIfTI: %s", nifti_path)

    try:
        # Cargar la imagen NIfTI
        logger.debug("Cargando el archivo NIfTI...")
        img = nib.load(nifti_path)
        data = img.get_fdata()
        logger.debug("Dimensiones de los datos cargados: %s", data.shape)

        # Validar que los datos no estén vacíos
        if data.size == 0:
            raise ValueError("El archivo NIfTI no contiene datos válidos.")

        # Seleccionar un corte en el eje Z (por ejemplo, el corte central)
        slice_index = data.shape[2] // 2
        logger.debug("Índice del corte seleccionado: %d", slice_index)
        slice_data = data[:, :, slice_index]

        # Crear una imagen PNG del corte
        logger.debug("Generando la imagen PNG del corte...")
        plt.figure(figsize=(6, 6))
        plt.axis('off')
        plt.imshow(slice_data.T, cmap='gray', origin='lower')
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        logger.debug("Imagen PNG generada correctamente.")

        # Pasar la imagen al frontend
        return render(request, 'diagnostico/visualizar_imagen.html', {
            'imagen': imagen,
            'img_base64': img_base64
        })

    except FileNotFoundError:
        error_message = "El archivo no se encontró. Por favor, verifica que el archivo exista."
        logger.error(error_message)
    except ValueError as ve:
        error_message = f"Error en el archivo: {str(ve)}"
        logger.error(error_message)
    except Exception as e:
        error_message = f"Error al procesar el archivo: {str(e)}"
        logger.error(error_message)

    # Mostrar un mensaje de error en el HTML
    return render(request, 'diagnostico/visualizar_imagen.html', {
        'imagen': imagen,
        'error': error_message
    })
def seleccionar_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'diagnostico/seleccionar_paciente.html', {'pacientes': pacientes})
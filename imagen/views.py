from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse
from .forms import ImagenMedicaForm
from .models import ImagenMedica
from pacientes.models import Paciente  # Importar el modelo Paciente
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
from pacientes.login import autenticacion, rol_requerido

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", message="Warning: 'partition' will ignore the 'mask' of the MaskedArray")

def reducir_resolucion(nii_path, output_path, target_shape=(64, 64, 64)):
    """
    Reduce la resolución de una imagen NIfTI y la guarda en un nuevo archivo.
    """
    if not os.path.exists(nii_path):
        raise FileNotFoundError(f"El archivo {nii_path} no existe o no se puede acceder.")

    # Cargar la imagen NIfTI
    img = nib.load(nii_path)

   
    return img
@autenticacion
@rol_requerido('Tecnico') 
@csrf_exempt  
def cargar_imagen(request):
    if request.method == 'POST':
        form = ImagenMedicaForm(request.POST, request.FILES)
        paciente_id = request.POST.get('paciente_id')
        if form.is_valid() and paciente_id:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            imagen = form.save(commit=False)
            imagen.paciente = paciente

            # Guardar la imagen original
            imagen.save()

            # Procesar la imagen para convertirla a PNG
            procesar_imagen(request, imagen.id)

            return redirect('reducir_imagen', paciente_id=paciente.id)
    else:
        form = ImagenMedicaForm()

    pacientes = Paciente.objects.all()
    return render(request, 'imagen/cargar_imagen.html', {'form': form, 'pacientes': pacientes})

def reducir_imagen(request, paciente_id=None):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    imagen = ImagenMedica.objects.filter(paciente=paciente).last()

    if not imagen:
        return render(request, 'imagen/reducir_imagen.html', {
            'error': 'No se encontró ninguna imagen asociada al paciente.'
        })

    ruta_original = imagen.archivo.path
    ruta_reducida = os.path.splitext(ruta_original)[0] + '_reducida.nii'

    try:
        img = nib.load(ruta_original)
        data = img.get_fdata()

        nib.save(nib.Nifti1Image(data, img.affine), ruta_reducida)

        # Guardar la imagen reducida como una nueva entrada en la base de datos
        nueva_imagen = ImagenMedica(
            nombre=f"{imagen.nombre}_reducida",
            archivo=os.path.relpath(ruta_reducida, settings.MEDIA_ROOT),
            paciente=paciente
        )
        nueva_imagen.save()

    except Exception as e:
        return render(request, 'imagen/reducir_imagen.html', {
            'imagen': imagen,
            'error': f'Error al procesar la imagen: {str(e)}'
        })

    return render(request, 'imagen/reducir_imagen.html', {'imagen': nueva_imagen})

def descargar_imagen(request, paciente_id=None, paciente_nombre=None):
    # Buscar el paciente por ID o nombre
    paciente = None
    if paciente_id:
        paciente = get_object_or_404(Paciente, id=paciente_id)
    elif paciente_nombre:
        paciente = get_object_or_404(Paciente, nombre=paciente_nombre)

    if paciente:
        # Buscar la última imagen asociada al paciente
        imagen = ImagenMedica.objects.filter(paciente=paciente).last()
        if not imagen:
            return render(request, 'imagen/reducir_imagen.html', {
                'error': 'No se encontró ninguna imagen asociada al paciente.'
            })

        # Verificar que la imagen esté en formato PNG
        if not imagen.archivo.name.endswith('.png'):
            return render(request, 'imagen/reducir_imagen.html', {
                'error': 'La imagen no está en formato PNG. Por favor, procese la imagen primero.'
            })

        # Descargar la imagen PNG
        png_path = os.path.join(settings.MEDIA_ROOT, imagen.archivo.name)
        if os.path.exists(png_path):
            return FileResponse(open(png_path, 'rb'), as_attachment=True, filename=os.path.basename(png_path))

    return render(request, 'imagen/reducir_imagen.html', {
        'error': 'No se pudo descargar la imagen.'
    })

def generar_vista_previa(nii_path, slice_index=100):
    if not os.path.exists(nii_path):
        raise FileNotFoundError(f"El archivo {nii_path} no existe o no se puede acceder.")

    img = nib.load(nii_path)
    data = img.get_fdata()
    slice_data = data[:, :, slice_index] if data.ndim == 3 else data[:, :]

    plt.axis('off')
    plt.imshow(slice_data.T, cmap='gray', origin='lower')
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def generar_vista_3d(nii_path):
    if not os.path.exists(nii_path):
        raise FileNotFoundError(f"El archivo {nii_path} no existe o no se puede acceder.")

    img = nib.load(nii_path)
    data = img.get_fdata()

   

    # Crear coordenadas espaciales para los ejes x, y, z
    x, y, z = np.mgrid[0:data.shape[0], 0:data.shape[1], 0:data.shape[2]]

    # Crear una visualización 3D interactiva con Plotly
    fig = go.Figure(data=go.Volume(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        value=data.flatten(),
        opacity=0.1,  # Transparencia
        surface_count=20  # Número de superficies
    ))

    # Guardar la visualización como un archivo HTML
    output_path = os.path.splitext(nii_path)[0] + '_3d.html'
    fig.write_html(output_path)
    return output_path

def generar_vistas_2d(nii_path):
    if not os.path.exists(nii_path):
        raise FileNotFoundError(f"El archivo {nii_path} no existe o no se puede acceder.")

    # Cargar la imagen NIfTI
    img = image.load_img(nii_path)

    # Generar vistas axiales, sagitales y coronales
    output_dir = os.path.dirname(nii_path)
    base_name = os.path.splitext(os.path.basename(nii_path))[0]

    axial_path = os.path.join(output_dir, f"{base_name}_axial.png")
    sagittal_path = os.path.join(output_dir, f"{base_name}_sagittal.png")
    coronal_path = os.path.join(output_dir, f"{base_name}_coronal.png")

    # Verificar si las vistas ya existen
    if not os.path.exists(axial_path):
        plotting.plot_img(img, display_mode='z', output_file=axial_path, title="Vista Axial")
    if not os.path.exists(sagittal_path):
        plotting.plot_img(img, display_mode='x', output_file=sagittal_path, title="Vista Sagital")
    if not os.path.exists(coronal_path):
        plotting.plot_img(img, display_mode='y', output_file=coronal_path, title="Vista Coronal")

    return {
        'axial': axial_path,
        'sagittal': sagittal_path,
        'coronal': coronal_path
    }

def visualizar_imagenes(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    # Obtener las últimas 6 imágenes asociadas al paciente desde la base de datos
    imagenes = ImagenMedica.objects.filter(paciente=paciente).order_by('-fecha_carga')[:6]

    visualizaciones = []
    for img in imagenes:
        visualizaciones.append({
            'nombre': img.nombre,
            'ruta': img.archivo.url  # Usar la URL del archivo para mostrarlo en el HTML
        })

    return render(request, 'diagnostico/visualizar_imagen.html', {'visualizaciones': visualizaciones})

def seleccionar_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'diagnostico/seleccionar_paciente.html', {'pacientes': pacientes})

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
def procesar_imagen(request, imagen_id):
    # Obtener la imagen desde la base de datos
    imagen = get_object_or_404(ImagenMedica, id=imagen_id)
    nifti_path = imagen.archivo.path

    try:
        # Cargar la imagen NIfTI
        img = nib.load(nifti_path)
        data = img.get_fdata()

        # Crear múltiples imágenes PNG de cortes axiales, sagitales y coronales
        output_dir = os.path.join(settings.MEDIA_ROOT, 'procesadas')
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(imagen.nombre)[0]

        # Generar cortes axiales, sagitales y coronales
        axial_path = os.path.join(output_dir, f"{base_name}_axial.png")
        sagittal_path = os.path.join(output_dir, f"{base_name}_sagittal.png")
        coronal_path = os.path.join(output_dir, f"{base_name}_coronal.png")

        plotting.plot_img(img, display_mode='z', output_file=axial_path, title="Vista Axial")
        plotting.plot_img(img, display_mode='x', output_file=sagittal_path, title="Vista Sagital")
        plotting.plot_img(img, display_mode='y', output_file=coronal_path, title="Vista Coronal")

        # Save the paths of the generated views in the database
        imagen.vista_axial = os.path.relpath(axial_path, settings.MEDIA_ROOT)
        imagen.vista_sagital = os.path.relpath(sagittal_path, settings.MEDIA_ROOT)
        imagen.vista_coronal = os.path.relpath(coronal_path, settings.MEDIA_ROOT)
        imagen.save()

        # Actualizar la ruta de los archivos procesados en la base de datos
        imagen.archivo.name = os.path.relpath(axial_path, settings.MEDIA_ROOT)  # Guardar solo la vista axial como referencia principal
        imagen.save()

        return render(request, 'imagen/reducir_imagen.html', {
            'imagen': imagen,
            'mensaje': 'Las imágenes han sido procesadas y convertidas a PNG.',
            'imagenes_generadas': [
                os.path.relpath(axial_path, settings.MEDIA_ROOT),
                os.path.relpath(sagittal_path, settings.MEDIA_ROOT),
                os.path.relpath(coronal_path, settings.MEDIA_ROOT)
            ]
        })

    except Exception as e:
        return render(request, 'imagen/reducir_imagen.html', {
            'imagen': imagen,
            'error': f"Error al procesar la imagen: {str(e)}"
        })

def mostrar_imagen(request, imagen_id):
    # Obtener la imagen desde la base de datos
    imagen = get_object_or_404(ImagenMedica, id=imagen_id)
    png_path = os.path.join(settings.MEDIA_ROOT, imagen.archivo.name)

    if not os.path.exists(png_path):
        return render(request, 'diagnostico/visualizar_imagen.html', {
            'imagen': imagen,
            'error': 'El archivo PNG no existe. Por favor, procese la imagen primero.'
        })

    return render(request, 'diagnostico/visualizar_imagen.html', {
        'imagen': imagen,
        'png_path': os.path.relpath(png_path, settings.MEDIA_ROOT)
    })
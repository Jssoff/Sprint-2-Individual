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

@csrf_exempt  
def cargar_imagen(request):
    if request.method == 'POST':
        form = ImagenMedicaForm(request.POST, request.FILES)
        paciente_id = request.POST.get('paciente_id')  # Obtener el ID del paciente del formulario
        if form.is_valid() and paciente_id:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            imagen = form.save(commit=False)
            imagen.paciente = paciente  # Asociar la imagen con el paciente

            # Mantener el nombre original del archivo
            original_name = os.path.basename(imagen.archivo.name)
            imagen.archivo.name = os.path.join('imagenes', original_name)

            # Guardar la imagen original
            imagen.save()

            # Reducir la resolución de la imagen
            ruta_original = imagen.archivo.path
            ruta_reducida = os.path.splitext(ruta_original)[0] + '_reducida.nii'
            reducir_resolucion(ruta_original, ruta_reducida)

            # Guardar la imagen reducida como una nueva entrada en la base de datos
            nueva_imagen = ImagenMedica(
                nombre=f"{imagen.nombre}_reducida",
                archivo=os.path.relpath(ruta_reducida, settings.MEDIA_ROOT),
                paciente=paciente
            )
            nueva_imagen.save()

            return redirect('reducir_imagen', paciente_id=paciente.id)  # Redirigir con paciente_id
    else:
        form = ImagenMedicaForm()
    
    pacientes = Paciente.objects.all()  # Obtener todos los pacientes
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
            return redirect('reducir_imagen', paciente_id=paciente.id)
        if imagen:
            return FileResponse(open(imagen.archivo.path, 'rb'), as_attachment=True, filename=imagen.nombre)

    return redirect('reducir_imagen')

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
    # Obtener las últimas 6 imágenes asociadas al paciente
    imagenes = ImagenMedica.objects.filter(paciente=paciente).order_by('-fecha_carga')[:6]

    visualizaciones = []
    for img in imagenes:
        try:
            # Generar vistas 2D de la imagen
            vistas = generar_vistas_2d(img.archivo.path)
            visualizacion = {
                'nombre': img.nombre,
                'vistas': vistas
            }
            visualizaciones.append(visualizacion)
        except Exception as e:
            visualizaciones.append({
                'nombre': img.nombre,
                'vistas': None,
                'error': str(e)
            })

    return render(request, 'imagen/visualizar_imagen.html', {'visualizaciones': visualizaciones})

def seleccionar_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'imagen/seleccionar_paciente.html', {'pacientes': pacientes})

def visualizar_imagenes_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    imagenes = ImagenMedica.objects.filter(paciente=paciente).order_by('-fecha_carga')

    visualizaciones = []
    for imagen in imagenes:
        if imagen.archivo.name.endswith('.nii') or imagen.archivo.name.endswith('.nii.gz'):
            nifti_path = os.path.join(settings.MEDIA_ROOT, imagen.archivo.name)

            if not os.path.exists(nifti_path):
                visualizaciones.append({
                    'nombre': imagen.nombre,
                    'error': f"El archivo {imagen.archivo.name} no existe o no se puede acceder."
                })
                continue

            try:
                # Generar vistas 2D preprocesadas si no existen
                vistas = generar_vistas_2d(nifti_path)

                # Agregar las vistas preprocesadas al contexto
                visualizaciones.append({
                    'nombre': imagen.nombre,
                    'vistas': vistas
                })
            except Exception as e:
                visualizaciones.append({
                    'nombre': imagen.nombre,
                    'error': f"Error al procesar el archivo: {str(e)}"
                })

    return render(request, 'imagen/visualizar_imagenes_paciente.html', {
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
        return render(request, 'imagen/visualizar_imagen.html', {
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
    return render(request, 'imagen/visualizar_imagen.html', {
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

        # Seleccionar un corte en el eje Z (por ejemplo, el corte central)
        slice_index = data.shape[2] // 2
        slice_data = data[:, :, slice_index]

        # Crear una imagen PNG del corte
        output_dir = os.path.join(settings.MEDIA_ROOT, 'procesadas')
        os.makedirs(output_dir, exist_ok=True)
        png_path = os.path.join(output_dir, f"{os.path.splitext(imagen.nombre)[0]}.png")

        plt.figure(figsize=(6, 6))
        plt.axis('off')
        plt.imshow(slice_data.T, cmap='gray', origin='lower')
        plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Actualizar la ruta del archivo procesado en la base de datos
        imagen.archivo.name = os.path.relpath(png_path, settings.MEDIA_ROOT)
        imagen.save()

        return render(request, 'imagen/reducir_imagen.html', {
            'imagen': imagen,
            'mensaje': 'La imagen ha sido procesada y convertida a PNG.'
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
        return render(request, 'imagen/visualizar_imagen.html', {
            'imagen': imagen,
            'error': 'El archivo PNG no existe. Por favor, procese la imagen primero.'
        })

    return render(request, 'imagen/visualizar_imagen.html', {
        'imagen': imagen,
        'png_path': os.path.relpath(png_path, settings.MEDIA_ROOT)
    })
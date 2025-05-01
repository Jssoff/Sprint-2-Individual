from django.shortcuts import render, get_object_or_404
from imagen.models import ImagenMedica
from pacientes.models import Paciente
import os
from django.conf import settings

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

def seleccionar_paciente(request):
    pacientes = Paciente.objects.all()
    return render(request, 'diagnostico/seleccionar_paciente.html', {'pacientes': pacientes})
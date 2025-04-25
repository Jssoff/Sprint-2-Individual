from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from .forms import ImagenMedicaForm
from .models import ImagenMedica
from pacientes.models import Paciente  # Importar el modelo Paciente
import nibabel as nib
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import os
@csrf_exempt  
def cargar_imagen(request):
    if request.method == 'POST':
        form = ImagenMedicaForm(request.POST, request.FILES)
        paciente_id = request.POST.get('paciente_id')  # Obtener el ID del paciente del formulario
        if form.is_valid() and paciente_id:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            imagen = form.save(commit=False)
            imagen.paciente = paciente  # Asociar la imagen con el paciente
            imagen.save()
            return redirect('reducir_imagen', paciente_id=paciente.id)  # Redirigir con paciente_id
    else:
        form = ImagenMedicaForm()
    
    pacientes = Paciente.objects.all()  # Obtener todos los pacientes
    return render(request, 'imagen/cargar_imagen.html', {'form': form, 'pacientes': pacientes})
@csrf_exempt  
def reducir_imagen(request, paciente_id=None, paciente_nombre=None):
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
        if imagen:
            ruta_original = imagen.archivo.path
            ruta_reducida = os.path.splitext(ruta_original)[0] + '_reducida.nii'

            try:
                # Cargar la imagen original
                img = nib.load(ruta_original)
                data = img.get_fdata()

                # Reducir la resolución
                reducido = data[::2, ::2, ::2]

                # Validar que la reducción no pierda información crítica
                if np.abs(np.mean(data) - np.mean(reducido)) > 0.1:  # Ajustar el umbral según sea necesario
                    return render(request, 'imagen/reducir_imagen.html', {
                        'imagen': imagen,
                        'error': 'La calidad de la imagen reducida no es aceptable.'
                    })

                # Guardar la imagen reducida en un nuevo archivo
                nib.save(nib.Nifti1Image(reducido, img.affine), ruta_reducida)

                # Actualizar la ruta del archivo reducido en el contexto
                imagen.archivo.name = os.path.basename(ruta_reducida)

            except Exception as e:
                return render(request, 'imagen/reducir_imagen.html', {
                    'imagen': imagen,
                    'error': f'Error al procesar la imagen: {str(e)}'
                })

        return render(request, 'imagen/reducir_imagen.html', {'imagen': imagen})

    return render(request, 'imagen/reducir_imagen.html', {'error': 'Paciente no encontrado.'})
@csrf_exempt  
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

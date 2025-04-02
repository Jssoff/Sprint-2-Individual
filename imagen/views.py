from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from .forms import ImagenMedicaForm
from .models import ImagenMedica
from pacientes.models import Paciente  # Importar el modelo Paciente
import nibabel as nib
import numpy as np
import os

def cargar_imagen(request):
    if request.method == 'POST':
        form = ImagenMedicaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('reducir_imagen')
    else:
        form = ImagenMedicaForm()
    return render(request, 'imagen/cargar_imagen.html', {'form': form})

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
        if imagen:
            return FileResponse(open(imagen.archivo.path, 'rb'), as_attachment=True, filename=imagen.nombre)

    return redirect('reducir_imagen')

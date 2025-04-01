from django.shortcuts import render, redirect
from .forms import ImagenMedicaForm
from .models import ImagenMedica
import nibabel as nib
import numpy as np

def cargar_imagen(request):
    if request.method == 'POST':
        form = ImagenMedicaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('reducir_imagen')
    else:
        form = ImagenMedicaForm()
    return render(request, 'imagen/cargar_imagen.html', {'form': form})

def reducir_imagen(request):
    imagen = ImagenMedica.objects.last()
    if imagen:
        ruta = imagen.archivo.path
        img = nib.load(ruta)
        data = img.get_fdata()
        reducido = data[::2, ::2, ::2]  # Reducir la resolución
        nib.save(nib.Nifti1Image(reducido, img.affine), ruta)
    return render(request, 'imagen/reducir_imagen.html', {'imagen': imagen})

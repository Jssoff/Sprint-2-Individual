"""
from django.shortcuts import render
import os
import torch
import nibabel as nib
import numpy as np
from django.http import JsonResponse
from django.conf import settings
from .modelo_epilepsia import EpilepsyCNN


def formulario_diagnostico(request):
    return render(request, 'diagnostico_IA/formulario.html')


def predecir_epilepsia(request):
    if request.method == 'POST' and 'imagen' in request.FILES:
        archivo = request.FILES['imagen']

        # Guardar archivo temporalmente
        ruta_temp = os.path.join(settings.BASE_DIR, 'temp.nii')
        with open(ruta_temp, 'wb') as f:
            for chunk in archivo.chunks():
                f.write(chunk)

        # Leer archivo .nii
        imagen = nib.load(ruta_temp)
        data = imagen.get_fdata()

        # Verifica y ajusta forma si es necesario
        if data.shape != (64, 64, 64):  # o el tamaño esperado
            from scipy.ndimage import zoom
            data = zoom(data, (64 / data.shape[0], 64 / data.shape[1], 64 / data.shape[2]))

        # Normalizar
        data = (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-6)
        data = np.expand_dims(data, axis=0)  # canal
        data = np.expand_dims(data, axis=0)  # lote
        tensor = torch.tensor(data).float()

        # Cargar modelo
        modelo = EpilepsyCNN()
        ruta_modelo = os.path.join(settings.BASE_DIR, 'diagnostico_IA', 'modelo', 'modelo_epilepsia.pth')
        modelo.load_state_dict(torch.load(ruta_modelo, map_location='cpu'))
        modelo.eval()

        with torch.no_grad():
            salida = modelo(tensor)
            pred = salida.argmax().item()

        diagnostico = "Epilepsia" if pred == 1 else "No Epilepsia"
        return JsonResponse({'resultado': diagnostico})

    return JsonResponse({'error': 'Método no permitido o archivo no enviado'}, status=400)
"""
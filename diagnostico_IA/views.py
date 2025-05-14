
from django.shortcuts import render
import torch
import nibabel as nib
import numpy as np
from django.http import JsonResponse
from django.conf import settings
from .modelo_epilepsia import EpilepsyCNN
from pacientes import *
import tempfile

def formulario_diagnostico(request):
    return render(request, 'diagnostico_IA/formulario.html')




def predecir_epilepsia(request):
    if request.method == 'POST' and 'imagen' in request.FILES:
        archivo = request.FILES['imagen']

        try:
            # ✅ Guardar archivo temporal de forma segura y automática
            with tempfile.NamedTemporaryFile(suffix=".nii") as temp_file:
                for chunk in archivo.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                # ✅ Leer archivo .nii desde el archivo temporal
                imagen = nib.load(temp_file.name)
                data = imagen.get_fdata()

            # Ajustar tamaño si es necesario
            if data.shape != (64, 64, 64):
                from scipy.ndimage import zoom
                data = zoom(data, (64 / data.shape[0], 64 / data.shape[1], 64 / data.shape[2]))

            # Normalizar y preparar tensor
            data = (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-6)
            data = np.expand_dims(data, axis=0)  # canal
            data = np.expand_dims(data, axis=0)  # lote
            tensor = torch.tensor(data).float()

            # Cargar modelo
            modelo = EpilepsyCNN()
            ruta_modelo = os.path.join(settings.BASE_DIR, 'diagnostico_IA', 'modelo', 'modelo_epilepsia.pth')
            modelo.load_state_dict(torch.load(ruta_modelo, map_location='cpu'))
            modelo.eval()

            # Predecir
            with torch.no_grad():
                salida = modelo(tensor)
                pred = salida.argmax().item()

            diagnostico = "Epilepsia" if pred == 1 else "No Epilepsia"
            return JsonResponse({'resultado': diagnostico})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido o archivo no enviado'}, status=400)

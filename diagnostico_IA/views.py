
from django.shortcuts import render
import torch
import nibabel as nib
import numpy as np
from django.conf import settings
from .modelo_epilepsia import EpilepsyCNN
from pacientes import *
import tempfile
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def formulario_diagnostico(request):
    return render(request, 'diagnostico_IA/formulario.html')







def predecir_epilepsia(request):
    if request.method == 'POST' and 'imagen' in request.FILES:
        archivo = request.FILES['imagen']

        try:
            with tempfile.NamedTemporaryFile(suffix=".nii") as temp_file:
                for chunk in archivo.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                imagen = nib.load(temp_file.name)
                data = imagen.get_fdata()

            # Resize si es necesario
            if data.shape != (64, 64, 64):
                from scipy.ndimage import zoom
                data = zoom(data, (64 / data.shape[0], 64 / data.shape[1], 64 / data.shape[2]))

            # Normalizar
            data = (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-6)
            data = np.expand_dims(data, axis=0)
            data = np.expand_dims(data, axis=0)
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

            # Convertir imagen central a PNG
            slice_index = 32  # Corte axial central
            slice_data = data[0, 0, :, :, slice_index]

            fig, ax = plt.subplots()
            ax.imshow(slice_data, cmap='gray')
            ax.axis('off')
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

            return render(request, 'diagnostico_IA/resultado.html', {
                'diagnostico': diagnostico,
                'imagen_base64': img_base64
            })

        except Exception as e:
            return render(request, 'diagnostico_IA/resultado.html', {
                'error': str(e)
            })

    return render(request, 'diagnostico_IA/resultado.html', {
        'error': 'Método no permitido o archivo no enviado'
    })

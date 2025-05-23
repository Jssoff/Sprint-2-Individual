
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





def predecir_epilepsia(request):{

}
   



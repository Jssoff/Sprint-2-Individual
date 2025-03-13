from django.shortcuts import render, get_object_or_404
from .models import Paciente
from historias_clinicas.models import HistoriaClinica
import time


def home(request):
    return render(request, 'Paciente/home.html')

def paciente_historial(request, paciente_id):
    start_time = time.time()
    
    paciente = get_object_or_404(Paciente, id=paciente_id)
    historias = HistoriaClinica.objects.filter(paciente=paciente)
    
    end_time = time.time()
    consulta_time = end_time - start_time
    
    context = {
        'paciente': paciente,
        'historias': historias,
        'consulta_time': consulta_time
    }
    return render(request, 'Paciente/paciente_historial.html', context)

def paciente_list(request):
    pacientes = Paciente.objects.all()
    context = {'paciente_list': pacientes}
    return render(request, 'Paciente/pacientes.html', context)


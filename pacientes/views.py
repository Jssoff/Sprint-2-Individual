from django.shortcuts import render, get_object_or_404, redirect
from .models import Paciente
from historias_clinicas.models import HistoriaClinica
import time
from .forms import PacienteForm
from django.http import HttpResponse

from .forms import PacienteForm
from .login import autenticacion

@autenticacion
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

def paciente_create(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('paciente_list')  
    else:
        form = PacienteForm()

    context = {'form': form}
    return render(request, 'Paciente/paciente_create.html', context)

def paciente_list(request):
    pacientes = Paciente.objects.all()
    context = {'paciente_list': pacientes}
    return render(request, 'Paciente/pacientes.html', context)

def paciente_delete(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
         # Verifica si el formulario es válido antes de eliminar
         # Esto es opcional, pero puede ser útil para validar datos antes de eliminar
        if form.is_valid():

         
         paciente.delete()
         return redirect('paciente_list')
        else:
                print(form.errors)
    else:
            form = PacienteForm()
    return render(request, 'Paciente/paciente_confirm_delete.html', {'paciente': paciente})

def healthCheck(request):
    return HttpResponse('ok')
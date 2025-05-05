from django.shortcuts import render, get_object_or_404, redirect
from .models import HistoriaUsuario, HistoriaClinica
from .forms import HistoriaUsuarioForm
from pacientes.models import Paciente

def historia_list(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    historias = HistoriaUsuario.objects.filter(paciente=paciente)
    context = {'historial_list': historias, 'paciente': paciente}
    return render(request, 'HistoriasUsuario/historias.html', context)


def crear_historia(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = HistoriaUsuarioForm(request.POST)
        if form.is_valid():
            historia = form.save(commit=False)
            historia.paciente = paciente
            historia.save()
            return redirect('paciente_historial', paciente_id=paciente.id)
    else:
        form = HistoriaUsuarioForm()

    return render(request, 'Paciente/crear_historia.html', {'form': form, 'paciente': paciente})

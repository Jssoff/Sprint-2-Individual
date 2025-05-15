from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from pacientes.models import Paciente
from .models import Foro
from .forms import ForoForm, ComentarioForm

def foro_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    foros = Foro.objects.filter(paciente=paciente).order_by('-fecha_creacion')

    if request.method == 'POST' and 'comentario' in request.POST:
        comentario_form = ComentarioForm(request.POST)
        if comentario_form.is_valid():
            comentario = comentario_form.save(commit=False)
            comentario.medico = request.session.get('usuario_autenticado') 
            
            foro_id = request.POST.get('foro_id')
            comentario.foro = get_object_or_404(Foro, id=foro_id)
            comentario.save()
            return redirect('foro_paciente', paciente_id=paciente.id)
    else:
        comentario_form = ComentarioForm()

    return render(request, 'foro/foro_paciente.html', {
        'paciente': paciente,
        'foros': foros,
        'comentario_form': comentario_form,
    })


def crear_foro(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = ForoForm(request.POST)
        if form.is_valid():
            foro = form.save(commit=False)
            foro.paciente = paciente
            foro.save()
            return redirect('foro_paciente', paciente_id=paciente.id)
    else:
        form = ForoForm()

    return render(request, 'foro/crear_foro.html', {
        'form': form,
        'paciente': paciente,
    })

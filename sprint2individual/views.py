
from django.shortcuts import render
from django.shortcuts import redirect
from sprint2individual.login import autenticacion

@autenticacion
def home(request):
    return render(request, 'sprint/home.html')


@autenticacion
def formulario_remoto(request):
    return redirect('https://diagnostico-ia-594687202111.us-central1.run.app/ia/formulario_predecir/')

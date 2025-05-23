
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from sprint2individual.login import autenticacion, rol_requerido
@autenticacion
def home(request):
    return render(request, 'sprint/home.html')
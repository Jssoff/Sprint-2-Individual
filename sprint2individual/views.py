
from django.shortcuts import render
from django.http import HttpResponse
from pacientes.login import autenticacion
@autenticacion
def home(request):
    return render(request, 'sprint/home.html')
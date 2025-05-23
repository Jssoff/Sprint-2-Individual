
from django.shortcuts import render
from django.http import HttpResponse
from sprint2individual.login import autenticacion

@autenticacion
def home(request):
    return render(request, 'sprint/home.html')
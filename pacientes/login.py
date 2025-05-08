from functools import wraps
from django.shortcuts import render, redirect 
from .models import Paciente
def autenticacion(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_autenticado'):
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper

USUARIOS_SIMULADOS = { 'Doctor': '123456', 'a': '987654', 'invitado': '1234' } 

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('clave')
        # Aquí puedes validar el usuario/clave
        if usuario == 'admin' and clave == '1234':  # Ejemplo
            request.session['usuario_autenticado'] = True
            return redirect('home')
        else:
            return render(request, 'Paciente/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'Paciente/login.html')
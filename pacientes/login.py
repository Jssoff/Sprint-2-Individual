from functools import wraps
from django.shortcuts import render, redirect 
from .models import Paciente
from django.contrib import messages

def autenticacion(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_autenticado'):
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper

USUARIOS_SIMULADOS = { 'Doctor': {'clave':'123456', 'rol': 'Doctor'},'Doctor Alfredo': {'clave':'123456', 'rol': 'Doctor'}, 'Doctor Juan': {'clave':'123456', 'rol': 'Doctor'}, 'Doctor Messi': {'clave':'123456', 'rol': 'Doctor'}, 'Doctor Cristiano': {'clave':'123456', 'rol': 'Doctor'}, 'Doctor Lamine Yamal': {'clave':'123456', 'rol': 'Doctor'},'a': {'clave':'987654', 'rol': 'Paciente'}, 'Tecnico': {'clave':'1234', 'rol': 'Tecnico'}, 'Tecnico 2': {'clave':'1234', 'rol': 'Tecnico'}, 'Tecnico 3 ': {'clave':'1234', 'rol': 'Tecnico'}, 'Tecnico 4': {'clave':'1234', 'rol': 'Tecnico'}, 'Tecnico 5 ': {'clave':'1234', 'rol': 'Tecnico'}} 

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('clave')
        # Aquí puedes validar el usuario/clave
        if usuario in USUARIOS_SIMULADOS and USUARIOS_SIMULADOS[usuario]['clave']== clave:
            request.session['usuario_autenticado'] = True
            request.session['rol'] = USUARIOS_SIMULADOS[usuario]['rol']
            return redirect('home')
        else:
            return render(request, 'Paciente/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'Paciente/login.html')

def rol_requerido(rol):
    def decorador(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.session.get('rol')==rol:
                return func(request, *args, **kwargs)
            messages.error(request, "No tienes la autorizacion para acceder a esta pagina.")
            return redirect('home')
        return wrapper
    return decorador

def logout_view(request):
    request.session.flush()  
    return redirect('login')

def registrarse(request):
    if request.method == 'Post':
        usuario= request.POST.get('usuario')
        contraseña = request.POST.get('contraseña')
        rol = request.POST.get ('rol')

        if usuario in USUARIOS_SIMULADOS:
            messages.error(request,"El usuario ya existe, use uno diferente")
        else:
            USUARIOS_SIMULADOS[usuario]= {'clave':contraseña, 'rol': rol}
            messages.success(request, "Usuario registrado con exito")
            return redirect('login')
    return render(request, 'Paciente/registo.html')
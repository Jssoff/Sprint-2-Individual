
from .models import Paciente

def obtener_pacientes():
    return list(Paciente.objects.values())

def obtener_paciente(paciente_id):
    return Paciente.objects.filter(id=paciente_id).values().first()

def crear_paciente(data):
    return Paciente.objects.create(
        nombre=data['nombre'],
        edad=data['edad'],
        tipo_sangre=data['tipo_sangre'],
        historia_clinica=data['historia_clinica'],
        alergias=data.get('alergias', ''),
        condiciones_medicas=data.get('condiciones_medicas', '')
    )

import json
from .models import HistoriaUsuario

def obtener_historias():
    return list(HistoriaUsuario.objects.values())

def obtener_historia(historia_id):
    return HistoriaUsuario.objects.filter(id=historia_id).values().first()

def crear_historia(data):
    return HistoriaUsuario.objects.create(
        paciente_id=data['paciente_id'],
        descripcion=data['descripcion'],
        tipo_historia=data['tipo_historia']
    )
        
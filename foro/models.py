from django.db import models
from .models import Paciente  
class Foro(models.Model):
    paciente = models.ForeignKey(Paciente, related_name='foros', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foro de {self.paciente.nombre} - {self.titulo}"

class Comentario(models.Model):
    foro = models.ForeignKey(Foro, related_name='comentarios', on_delete=models.CASCADE)
    medico = models.CharField(max_length=255)  
    texto = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.medico.username} - {self.fecha_comentario}"

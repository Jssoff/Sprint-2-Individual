from django.db import models
from pacientes.models import Paciente  

class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="historias_clinicas")
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    tipo_historia = models.CharField(max_length=50, choices=[
        ('Crisis Epiléptica', 'Crisis Epiléptica'),
        ('Consulta', 'Consulta'),
        ('Tratamiento', 'Tratamiento'),
        ('Otro', 'Otro'),
    ])

    def __str__(self):
        return f"{self.tipo_historia} de {self.paciente.nombre} - {self.fecha.strftime('%Y-%m-%d')}"

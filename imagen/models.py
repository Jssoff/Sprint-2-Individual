from django.db import models
from pacientes.models import Paciente

class ImagenMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='imagenes/')
    fecha_carga = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

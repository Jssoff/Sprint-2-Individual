from django.db import models
from pacientes.models import Paciente  # Importar el modelo Paciente

class ImagenMedica(models.Model):
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='imagenes/')
    fecha_carga = models.DateTimeField(auto_now_add=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='imagenes')  # Relación con Paciente
    vista_axial = models.FileField(upload_to='imagenes/', null=True, blank=True)
    vista_sagital = models.FileField(upload_to='imagenes/', null=True, blank=True)
    vista_coronal = models.FileField(upload_to='imagenes/', null=True, blank=True)

    def __str__(self):
        return self.nombre
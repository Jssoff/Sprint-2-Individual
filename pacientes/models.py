from django.db import models 

class Paciente(models.Model):
    TIPO_SANGRE_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    TIPO_DOCUMENTO_CHOICES = [
        ('RC', 'Registro Civil'),
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería')
    ]
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=20, unique=True, default='123456789')
    nombre = models.CharField(max_length=255)
    edad = models.IntegerField()
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE_CHOICES, default='O+')
    historia_clinica = models.CharField(max_length=50, unique=True)
    alergias = models.TextField(blank=True, null=True)
    condiciones_medicas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} (HC: {self.historia_clinica})"

from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['tipo_documento', 'numero_documento', 'nombre', 'edad', 'tipo_sangre', 'historia_clinica', 'alergias', 'condiciones_medicas']

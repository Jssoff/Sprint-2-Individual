from django import forms
from .models import HistoriaClinica

class HistoriaUsuarioForm(forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = ['descripcion', 'tipo_historia', 'fecha']

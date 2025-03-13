from django import forms
from .models import HistoriaUsuario

class HistoriaUsuarioForm(forms.ModelForm):
    class Meta:
        model = HistoriaUsuario
        fields = ['descripcion', 'tipo_historia']

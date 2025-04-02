from django import forms
from .models import ImagenMedica

class ImagenMedicaForm(forms.ModelForm):
    class Meta:
        model = ImagenMedica
        fields = ['nombre', 'archivo']

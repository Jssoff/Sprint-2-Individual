from django import forms
from .models import ImagenMedica, Paciente

class ImagenMedicaForm(forms.ModelForm):
    class Meta:
        model = ImagenMedica
        fields = ['nombre', 'archivo', 'paciente']
    def clean_paciente(self):
        paciente = self.cleaned_data.get('paciente')
        if not Paciente.objects.filter(id=paciente.id).exists():
            raise forms.ValidationError('El paciente seleccionado no existe.')
        return paciente


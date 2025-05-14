from django import forms
from .models import Foro, Comentario

class ForoForm(forms.ModelForm):
    class Meta:
        model = Foro
        fields = ['titulo', 'descripcion']

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario aquí...'}),
        }

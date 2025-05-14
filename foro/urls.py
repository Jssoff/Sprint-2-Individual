from django.urls import path
from . import views

urlpatterns = [
    path('paciente/<int:paciente_id>/foros/', views.foro_paciente, name='foro_paciente'),
    path('paciente/<int:paciente_id>/crear_foro/', views.crear_foro, name='crear_foro'),
]

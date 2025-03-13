from django.urls import path
from .views import paciente_historial

urlpatterns = [
    path('paciente/historial/<int:paciente_id>/', paciente_historial, name='paciente_historial'),
]

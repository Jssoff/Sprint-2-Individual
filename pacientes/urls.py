
from django.urls import path
from .views import paciente_list, paciente_historial

urlpatterns = [
    path('', paciente_list, name='paciente_list'),  
    path('paciente/historial/<int:paciente_id>/', paciente_historial, name='paciente_historial'),
]

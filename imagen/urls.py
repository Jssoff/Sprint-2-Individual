from django.urls import path
from . import views

urlpatterns = [
    path('cargar/', views.cargar_imagen, name='cargar_imagen'),
    path('reducir/<int:paciente_id>/', views.reducir_imagen, name='reducir_imagen'),
    path('descargar/<int:paciente_id>/', views.descargar_imagen, name='descargar_imagen'),  # Nueva ruta
]

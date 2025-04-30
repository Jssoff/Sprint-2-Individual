from django.urls import path
from . import views

urlpatterns = [
    path('cargar/', views.cargar_imagen, name='cargar_imagen'),
    path('reducir/<int:paciente_id>/', views.reducir_imagen, name='reducir_imagen'),
    path('descargar/<int:paciente_id>/', views.descargar_imagen, name='descargar_imagen'),  
    path('visualizar/<int:paciente_id>/', views.visualizar_imagenes, name='visualizar_imagenes'),
    path('seleccionar_paciente/', views.seleccionar_paciente, name='seleccionar_paciente'),
    path('visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='visualizar_imagenes_paciente'),
]

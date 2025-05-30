from django.urls import path
from . import views


urlpatterns = [
    path('dj-cargar/', views.cargar_imagen, name='dj_cargar_imagen'),
    path('dj-reducir/<int:paciente_id>/', views.reducir_imagen, name='dj_reducir_imagen'),
    path('dj-descargar/<int:paciente_id>/', views.descargar_imagen, name='dj_descargar_imagen'),  
    path('dj-imagen/<int:imagen_id>/', views.visualizar_imagen, name='dj_visualizar_imagen'),
    path('dj-visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='dj_visualizar_imagenes_paciente'),
]
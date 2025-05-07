from django.urls import path
from . import views
from .views import analizar_imagen

urlpatterns = [
    path('cargar/', views.cargar_imagen, name='cargar_imagen'),
    path('reducir/<int:paciente_id>/', views.reducir_imagen, name='reducir_imagen'),
    path('descargar/<int:paciente_id>/', views.descargar_imagen, name='descargar_imagen'),  
    path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
    path('visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='visualizar_imagenes_paciente'),
    path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
    path('analizar/<int:imagen_id>/', analizar_imagen, name='analizar_imagen'),
]
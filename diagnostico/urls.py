from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='visualizar_imagenes_paciente'),
    path('seleccionar_paciente/', views.seleccionar_paciente, name='seleccionar_paciente'),
    path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
    path('entrenar-modelo/', views.entrenar_modelo_diagnostico, name='entrenar_modelo_diagnostico'),
    path('analizar-imagenes/<int:paciente_id>/', views.analizar_imagenes_paciente, name='analizar_imagenes_paciente'),
    path('analizar-resultados/<int:paciente_id>/', views.analizar_imagenes_paciente_resultados, name='analizar_imagenes_paciente_resultados'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
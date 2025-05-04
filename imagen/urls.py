from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cargar/', views.cargar_imagen, name='cargar_imagen'),
    path('reducir/<int:paciente_id>/', views.reducir_imagen, name='reducir_imagen'),
    path('descargar/<int:paciente_id>/', views.descargar_imagen, name='descargar_imagen'),  
    #path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
    #path('visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='visualizar_imagenes_paciente'),
    #path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
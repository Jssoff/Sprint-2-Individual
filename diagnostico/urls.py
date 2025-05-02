from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('visualizar_paciente/<int:paciente_id>/', views.visualizar_imagenes_paciente, name='visualizar_imagenes_paciente'),
    path('seleccionar_paciente/', views.seleccionar_paciente, name='seleccionar_paciente'),
    path('imagen/<int:imagen_id>/', views.visualizar_imagen, name='visualizar_imagen'),
    path('health/', views.healthCheck, name= 'health'),	

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

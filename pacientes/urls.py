from django.urls import path
from .views import home, paciente_list, paciente_historial
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'), 
    path('pacientes/', paciente_list, name='paciente_list'),
    path('paciente/historial/<int:paciente_id>/', paciente_historial, name='paciente_historial'),
    path('health-check/', views.healthCheck),	
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

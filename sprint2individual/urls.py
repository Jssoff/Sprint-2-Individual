from django.urls import path, include
from .views import home, paciente_list, paciente_historial
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import login

urlpatterns = [
    path('login/', login.login_view, name='login'),
    path('registro/', login.registrarse, name='registro'),
    path('logout/', login.logout_view, name='logout'),
    path('', home, name='home'), 
    
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('pacientes/', include('pacientes.urls')),
    path('imagen/', include('imagen.urls')),  
    path('diagnostico/', include('diagnostico.urls')),
    path('historias/', include('historias_clinicas.urls')),
    path('foro/', include('foro.urls')),
    path('diagnostico_IA/', include('diagnostico_IA.urls')),

]
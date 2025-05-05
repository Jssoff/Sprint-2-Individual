from django.urls import path
from .views import historia_list, crear_historia

urlpatterns = [
    path('api/historias/', historia_list, name='historia_list'),
    path('api/historia/crear/<int:paciente_id>/', crear_historia, name='crear_historia'),
]

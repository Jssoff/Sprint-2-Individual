from django.urls import path
from . import views

urlpatterns = [
    path('cargar/', views.cargar_imagen, name='cargar_imagen'),
    path('reducir/', views.reducir_imagen, name='reducir_imagen'),
]

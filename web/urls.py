from django.urls import path
from . import views

urlpatterns = [
    path ('Inicio/', views.index, name='inicio'),
]
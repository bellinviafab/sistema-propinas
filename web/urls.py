from django.urls import path
from . import views

urlpatterns = [
    path ('Inicio/', views.index, name='inicio'),
    path ('FAQ/', views.about, name='faq'),
]
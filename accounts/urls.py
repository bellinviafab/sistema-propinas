from django.urls import path
from . import views

urlpatterns =  [
    path('accounts/crearcuenta/', views.crearcc, name='crear_cuenta'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('accounts/login/', views.signin, name='login'),
    path('accounts/logout/', views.signout, name='logout'),

]
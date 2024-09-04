from django.urls import path
from . import views 

urlpatterns =  [
    path('crearcuenta/', views.crearcc, name='crear_cuenta'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),  
    path('crearcuenta/agregar_comercio/', views.regcom, name='agregar_comercio'),
    path('crearcuenta/agregar_comercio/regempleado', views.regemp, name='reg_empleados'),
    path('logout/', views.signout, name='logout'),
 ]
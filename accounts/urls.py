from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns =  [
    path('accounts/crearcuenta/', views.crearcc, name='crear_cuenta'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('accounts/login/', views.signin, name='login'),
    path('accounts/logout/', views.signout, name='logout'),
    path('accounts/perfil/', views.ver_perfil, name='ver_perfil'),
    path('accounts/editar_perfil/', views.editar_perfil_propietario, name='editar_perfil_propietario'),
    path('accounts/editar_perfil_empleado/', views.editar_perfil_empleado, name='editar_perfil_empleado'),
    path('accounts/cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('accounts/olvidar_contrasena/', views.olvidar_contrasena, name='olvidar_contrasena'),
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), 
         name='password_reset_confirm'),
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name='password_reset_complete'),

]
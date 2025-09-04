from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('Miproppi/', views.signin, name='login'),
    path('MiProppi/perfil_config_/', views.perfil_usercom_config, name='perfil_usercom_config'),
    path('Miproppi/mis_comercios', views.cuenta, name= 'mis_comercios'),
    path('Miproppi/mis_comercios/<int:comercio_id>/', views.detalle_comercio, name='detalle_comercio'),
    path('Miproppi/mis_comercios/agregar_empleado/<int:comercio_id>/', views.agregar_emp, name='agregar_emp'),
    path('subir_imagen_comercio/<int:comercio_id>/', views.subir_imagen_comercio, name='subir_imagen_comercio'),
    path('Miproppi/mis_comercios/eliminar_emp/<int:comercio_id>', views.eliminar_emp, name = 'eliminar_emp'),
    path('Proppiempleado/login/', views.login_empleado, name='login_empleado'),
    path('Proppi/perfil/',views.perfil, name='perfil'),
    path('Proppi/recuperar_contraseña', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('Proppi/cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena')
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


#path('Miproppi/mis_comercios/agregar_emp/<int:comercio_id>', views.agregar_emp, name='agregar_emp'),
    #path('Proppi/perfil_config/', views.configurar_perfil, name='config_empleado'),
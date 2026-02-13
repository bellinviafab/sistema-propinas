from django.urls import path
from . import views 
from Adherircom import models

urlpatterns = [
    path('deposita_propina/<int:comercio_id>/', views.deposita_propina, name='deposita_propina'),
    path('pago_exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago_fallido/', views.pago_fallido, name='pago_fallido'),
    path('pago_pendiente/', views.pago_pendiente, name='pago_pendiente'),
    path('webhook/', views.webhook, name = 'webhook'),
    path('Proppi/faq', views.faq, name='faq'),
    path('Proppi/contacto', views.contacto, name='contacto'),
]


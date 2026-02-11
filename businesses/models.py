from django.db import models
from django.conf import settings


# Create your models here.

class Comercio(models.Model):
    nombre_comercio = models.CharField(max_length=100)
    tipo_comercio = models.CharField(max_length=20, choices=[('restaurante', 'Restaurante'), ('bar', 'Bar'), ('cafe', 'Café'), ('otros', 'Otros')], default='restaurante')
    nombre_calle = models.CharField(max_length=50, null = False)
    numero_calle = models.PositiveIntegerField(null=False)
    imagen = models.ImageField(upload_to='comercio_images/', blank=True)
    ccreada = models.DateTimeField(auto_now_add=True, blank=True)
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comercios')
    ciudad = models.ForeignKey('core.Ciudad', on_delete = models.SET_NULL, null = True)

    def __str__(self):
        return f"{self.nombre_comercio}  -  {self.propietario.username}"
    

class codigo_qr(models.Model):
    comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='codigo_qr', blank=True)
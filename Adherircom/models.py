from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from core.models import Ciudad,Provincia
from accounts.models import Empleado, Propietario



# Create your models here.d
"""class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cuit = models.CharField(max_length=11,blank=True)

    def __str__(self):
        return self.user.username"""


class Comercio(models.Model):
    nombre_comercio = models.CharField(max_length=100)
    tipo_comercio = models.CharField(max_length=20, choices=[('restaurante', 'Restaurante'), ('bar', 'Bar'), ('cafe', 'Café'), ('otros', 'Otros')], default='restaurante')
    nombre_calle = models.CharField(max_length=50, null = False)
    numero_calle = models.PositiveIntegerField(null=False)
    imagen = models.ImageField(upload_to='comercio_images/', blank=True)
    codigo_qr = models.ImageField(upload_to='codigo_qr', blank=True)
    ccreada = models.DateTimeField(auto_now_add=True, blank=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comercios')
    ciudad = models.ForeignKey(Ciudad, on_delete = models.SET_NULL, null = True)

    def __str__(self):
        return f"{self.nombre_comercio}  -  {self.propietario.username}"
    
    def reset_ingresos_diarios(self):
        self.ingresos_diarios=0
        self.save()
    
class IngresoDiario(models.Model):
    id_comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total_diario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('id_comercio','fecha')


class Propina(models.Model):
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=40, null = False)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    pagado = models.BooleanField(default=False)


    class Meta:
        indexes = [
            models.Index(fields=['fecha','comercio'])
        ]

DIAS_SEMANA_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo')
]

class TieneAsignado(models.Model): 
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    fecha_ingreso = models.DateField()

    class Meta:
        unique_together = ('id_empleado','id_comercio','fecha_ingreso')

class HorarioTrabajo(models.Model):  #HorarioTrabajo->tieneAsignado
    asignacion = models.ForeignKey(TieneAsignado, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    cantidad_horas = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        dia = dict(DIAS_SEMANA_CHOICES).get(self.dia_semana)
        return f"{self.asignacion.id_empleado.user.first_name} - {dia} ({self.cantidad_horas} horas)"


class RepartoPropina(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    fecha_reparto = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=False)

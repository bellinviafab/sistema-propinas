from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator


# Create your models here.d
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cuit = models.CharField(max_length=11,blank=True)

    def __str__(self):
        return self.user.username
    

class Comercio(models.Model):
    nombre_comercio = models.CharField(max_length=100)
    tipo_comercio = models.CharField(max_length=20, choices=[('restaurante', 'Restaurante'), ('bar', 'Bar'), ('cafe', 'Café'), ('otros', 'Otros')], default='restaurante')
    direccion = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='comercio_images/', blank=True)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    ingresos_diarios = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    ingresos_total = models.DecimalField(max_digits=10, decimal_places=2,blank=True, default=0)
    codigo_qr = models.ImageField(upload_to='codigo_qr', blank=True)
    codigo_qr_entrada = models.ImageField(upload_to='codigo_qr_entrada', blank=True)
    ccreada = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comercios')

    def __str__(self):
        return self.nombre_comercio + ' - ' + self.user.username
    
    def setcomercio_data(self,nombre, tipo, direccion, ciudad, provincia, imagen=None):
        self.nombre_comercio = nombre
        self.tipo_comercio = tipo
        self.direccion = direccion
        self.ciudad = ciudad
        self.provincia = provincia
        if imagen:
            self.imagen=imagen
        self.save()

    def reset_ingresos_diarios(self):
        self.ingresos_diarios=0
        self.save()
    
    def actualiza_ingresos_diarios(self,monto):
        try:
            self.ingresos_diarios += monto
            self.save()
        except Exception as e:
            raise Exception(f"Error al actualizar ingresos del comercio: {str(e)}")
    
class Propina(models.Model):
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
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
    
class Empleado(models.Model):
    nombre = models.CharField(max_length=50)
    email = models.EmailField(max_length=35)
    alias = models.CharField(max_length=40)
    cuil = models.CharField(max_length=20, unique=True)
    ingresos_diarios = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comercios = models.ManyToManyField(Comercio, related_name='empleados')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre + ' - ' + self.comercios.nombre_comercio

class HorarioTrabajo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='horarios_empleado')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    cantidad_horas = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        dia = dict(DIAS_SEMANA_CHOICES).get(self.dia_semana)
        return f"{self.empleado.nombre} - {dia} ({self.cantidad_horas} horas)"
















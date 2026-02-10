from django.db import models
from django.contrib.auth.models import User
from core.models import Ciudad, Provincia

# Create your models here.
rol_choices = {
        ('propietario','Propietario'),
        ('empleado', 'Empleado'),
    }

class Propietario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null = True)



class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = False)
    alias = models.CharField(max_length=30)

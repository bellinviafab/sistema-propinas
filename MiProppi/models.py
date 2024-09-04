from django.db import models
from Adherircom.models import *
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class CheckInOut(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='checkinouts')
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    hora_entrada = models.DateTimeField()
    hora_salida = models.DateTimeField(null=True, blank=True)
    completado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.hora_salida:
            dia_semana = self.hora_entrada.weekday() 
            horario = HorarioTrabajo.objects.get(empleado=self.empleado, dia_semana=dia_semana)
            self.hora_salida = self.hora_salida + timedelta(hours=float(horario.cantidad_horas))

        if not self.completado and self.hora_salida <= timezone.now():
            self.completado = True
        
        super(CheckInOut, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.comercio.nombre_comercio} - {self.hora_entrada} to {self.hora_salida}"
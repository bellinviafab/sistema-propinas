from django.db import models
# Create your models here.

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
    empleado = models.ForeignKey('accounts.Empleado', on_delete=models.CASCADE)
    comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    fecha_ingreso = models.DateField()

    class Meta:
        unique_together = ('empleado','comercio','fecha_ingreso')

class HorarioTrabajo(models.Model):  #HorarioTrabajo->tieneAsignado
    asignacion = models.ForeignKey(TieneAsignado, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    cantidad_horas = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        dia = dict(DIAS_SEMANA_CHOICES).get(self.dia_semana)
        return f"{self.asignacion.empleado.user.first_name} - {dia} ({self.cantidad_horas} horas)"
from django.db import models
import uuid
# Create your models here.




class IngresoDiario(models.Model):
    id_comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    total_diario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('id_comercio','fecha')

    def __str__(self):
        return f"{self.id_comercio} - {self.fecha.strftime('%Y-%m-%d')} - {self.total_diario}"


class Propina(models.Model):
    ESTADOS = [
        ('AP', 'Aprobado'),
        ('PE', 'Pendiente'),
        ('RE', 'Rechazado'),
        ('DE', 'Devuelto'),
    ]

    comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=40, null = False)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    estado = models.CharField(max_length=2, choices=ESTADOS, default='PE')
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)
    #Relacion con el codigo qr para saber de que mesa/zona vino la propina
    qr_origen = models.ForeignKey('businesses.CodigoQr', on_delete=models.SET_NULL, null=True, blank=True)
    turno = models.ForeignKey('staff.TieneAsignado', on_delete=models.SET_NULL, null=True, related_name='propinas')
    # ID único que enviamos a la API (Nave/MP) para el Webhook
    referencia_externa = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # ID que nos devuelve la pasarela una vez pagado
    id_transaccion_pasarela = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['fecha','comercio'])
        ]

    def __str__(self):
        return f"{self.nombre_cliente} - {self.monto} ({self.get_estado_display()})"

class RepartoPropina(models.Model):  
    ESTADOS_PAGO = [
        ('PE', 'Pendiente'),
        ('EN', 'Enviado'),
        ('PA', 'Pagado'),
        ('RE', 'Rechazado'),
    ]

    empleado = models.ForeignKey('accounts.Empleado', on_delete=models.CASCADE)
    comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    fecha_reparto = models.DateTimeField(auto_now_add=True)
    monto_neto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=2, choices=ESTADOS_PAGO, default='PE')
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.empleado} - {self.monto_neto} ({self.get_estado_display()})"
from django.db import models

# Create your models here.

class cuentamain(models.Model):
    ingresosproppi = models.DecimalField(max_digits=10, decimal_places=2)
    totingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totalusuarios = models.IntegerField(default=0)
    totalcomercios = models.IntegerField(default=0)
    totalempleados = models.IntegerField(default=0)

    def add_totusuarios(self):
        self.totalusuarios +=1
        self.save()
    
    def add_totalcomercios(self):
        self.totalcomercios +=1
        self.save()

    def add_empleado(self):
        self.totalempleados +=1
        self.save()
    
    def add_totalempleados(self, cant_empleados):
        self.totalempleados += cant_empleados
        self.save()
    

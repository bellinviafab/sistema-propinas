from django.db import models

# Create your models here.

class Provincia(models.Model):
    nombre = models.CharField(max_length=100, unique= True)

    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nombre', 'provincia')

    def __str__(self):
        return f"{self.nombre}, {self.provincia.nombre}"
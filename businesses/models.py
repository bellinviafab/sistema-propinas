from django.db import models
from django.conf import settings
from django.utils.text import slugify
import qrcode
from io import BytesIO
from django.core.files import File

# Create your models here.

TIPO_REPARTO = [
    ('proporcional_horas', 'Proporcional a las horas trabajadas'),
    ('igualitario', 'Reparto igualitario entre los empleados'),
]


class Comercio(models.Model):
    #Datos del comercio
    nombre_comercio = models.CharField(max_length=100)
    tipo_comercio = models.CharField(max_length=20, choices=[('restaurante', 'Restaurante'), ('bar', 'Bar'), ('cafe', 'Café'), ('otros', 'Otros')], default='restaurante')
    nombre_calle = models.CharField(max_length=50, null = False)
    numero_calle = models.PositiveIntegerField(null=False)
    ciudad = models.ForeignKey('core.Ciudad', on_delete = models.SET_NULL, null = True)
    imagen = models.ImageField(upload_to='comercio_images/', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    cuit = models.CharField(max_length=11, unique=True, null=True, blank=True)
    #Slug
    slug = models.SlugField(max_length=100, unique=True)
    #Configuración del comercio
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comercios')
    activo = models.BooleanField(default=True)
    algoritmo_reparto = models.CharField(max_length=20, choices = TIPO_REPARTO, default = 'proporcional_horas')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre_comercio)
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.nombre_comercio}  -  {self.propietario.username}"
    

class CodigoQr(models.Model):
    comercio = models.ForeignKey('businesses.Comercio', on_delete=models.CASCADE)
    nombre_identificador = models.CharField(max_length=100, default = "General")
    imagen = models.ImageField(upload_to='codigo_qr', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.imagen:
            # 1. Armamos la URL a la que apuntará el QR (La Landing de Proppi)
            # Nota: Cambiar "proppi.com.ar" por el dominio local durante desarrollo si es necesario
            url_destino = f"https://proppi.com.ar/pago/{self.comercio.slug}/"
            
            # 2. Generamos el código QR
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url_destino)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 3. Guardamos la imagen en memoria y la asignamos al ImageField
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            nombre_archivo = f"qr_{self.comercio.slug}_{slugify(self.nombre_identificador)}.png"
            self.imagen.save(nombre_archivo, File(buffer), save=False)
            
        super().save(*args, **kwargs)
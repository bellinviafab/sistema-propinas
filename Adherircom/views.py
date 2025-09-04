from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.db import IntegrityError, transaction
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
import qrcode, io, string, random, smtplib
from django.urls import reverse
from django.http import HttpRequest
from email.mime.text import MIMEText
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.db import transaction
import logging
from django.db.models import F
from django.contrib.auth.models import Group
from Autotask.tasks import enviacorreo

# Create your views here.
def crearcc(request):
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "crearcuenta.html", {"form": form})
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): #Si formulario enviado por el POST es valida
            try:
                user = form.save(commit=False)
                user.is_active = False #Desactivar cuenta hasta que se confirme el correo
                user.save()
                

                enviarcorreocc(request, user)
                grupo_usuario_comercio = Group.objects.get(name='usuario-comercio')
                user.groups.add(grupo_usuario_comercio)
                return render(request, 'confirmar_cuenta.html')                
            except IntegrityError: # Usuario ya existe
                return render(
                    request,
                    "crearcuenta.html",
                    {"form": form, "error": "Usuario y/o Mail ya estan registrados"},
                )
        else: #Formulario no valido
            return render(
                request,
                "crearcuenta.html",
                {"form": form, "error": form.errors},
            )       

def enviarcorreocc(request, user):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    current_site = get_current_site(request)
    mail_subject = 'Activa tu cuenta'
    message = render_to_string('activarcuenta.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    destinatario = user.email
    mensaje = MIMEText(message, 'html')
    mensaje['Subject'] = mail_subject
    mensaje['From'] = smtp_user
    mensaje['To'] = destinatario

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, destinatario, mensaje.as_string())

def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, '¡Tu cuenta ha sido activada correctamente! Ahora puedes iniciar sesión.')
        return redirect('login')  # Redirige a la página de inicio de sesión
    else:
        return render(request, 'activacion_invalida.html')  # Muestra una página de error de activación inválida


@login_required
@permission_required("Adherircom.add_comercio")
def regcom(request):
     if request.method == 'GET':
        return render(request, 'regcomercio.html',{
            'form' : Registrocomercio()
         })
     else:
        form = Registrocomercio(request.POST)   #recibe los datos mediante el metodo post y se los pasa al fom registrocomerico
        print("Formulario recibido")
        if form.is_valid(): 
            comercio = form.save(commit=False)  # No guarda aún, solo crea una instancia
            comercio.propietario = request.user  # Asigna el usuario actual como propietario del comercio  # Genera el código QR para el comercio
            comercio.save()
            asignaqr(comercio)  #asignaqr_entrada(comercio) 
            return redirect('mis_comercios')  ##regemp
        else:
            print("Formulario no valido")
            print(form.errors)
            return render(request, 'regcomercio.html',{
            'form' : form
             })     
        

def asignaqr(dato_comercio):
    base_domain = settings.BASE_DOMAIN
    path = reverse('deposita_propina', kwargs={'comercio_id': dato_comercio.id})
    url_comercio = f"{base_domain}{path}"
    print(url_comercio)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url_comercio)   #El qr contendrá la info de cada comercio
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    dato_comercio.codigo_qr.save(f'qr_comercio_{dato_comercio.nombre_comercio}.png',ContentFile(buffer.getvalue()), save=True)


""""
#Fuera de mvp(A quitar)
def asignaqr_entrada(dato_comercio, request=HttpResponse()):
    base_domain = settings.BASE_DOMAIN
    path = reverse('checkin', kwargs={'comercio_id': dato_comercio.id})
    url_comercio = f"{base_domain}{path}"
    print(url_comercio)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url_comercio)   # El QR contendrá la info de cada comercio para check-in
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    dato_comercio.codigo_qr_entrada.save(f'qr_entrada_{dato_comercio.nombre_comercio}.png', ContentFile(buffer.getvalue()), save=True)


"""
def signout(request):
     logout(request)
     return redirect('inicio')
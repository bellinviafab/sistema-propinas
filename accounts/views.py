import smtplib
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from Proppi import settings
from .forms import CustomUserCreationForm
from django.contrib.auth import login, logout
from django.db import IntegrityError
import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

# Create your views here.
def crearcc(request):
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "accounts/crearcuenta.html", {"form": form})
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
                return render(request, 'accounts/confirmar_cuenta.html')                
            except IntegrityError: # Usuario ya existe
                return render(
                    request,
                    "accounts/crearcuenta.html",
                    {"form": form, "error": "Usuario y/o Mail ya estan registrados"},
                )
        else: #Formulario no valido
            return render(
                request,
                "accounts/crearcuenta.html",
                {"form": form, "error": form.errors},
            )      
        
def enviarcorreocc(request, user):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    current_site = get_current_site(request)
    mail_subject = 'Activa tu cuenta'
    message = render_to_string('accounts/activarcuenta.html', {
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
        return render(request, 'accounts/activacion_invalida.html')  # Muestra una página de error de activación inválida

def signin(request): #Comprobar en base de datos si datos existen  Añadir olvide contraseña
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {
        'form' : form
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render(request, 'accounts/login.html', {
                'form' : AuthenticationForm,
                'error' : 'Usuario y/o contraseña son incorrectos'
            })
        else: #Verifica que pertenezca al grupo usuario-comercio o al usuario-empleado
            if user.groups.filter(name='usuario-comercio').exists():
                login(request,user)
                return redirect('inicio')
            else:
                if user.groups.filter(name='usuario-empleado').exists():
                    login(request,user)
                    return redirect('inicio')
                else:
                    return render(request, 'accounts/login.html', {
                    'form' : AuthenticationForm,
                    'error': 'No tienes permisos para acceder como comercio o empleado.'
                    })

def signout(request):
     logout(request)
     return redirect('inicio')


            
            
            
            
            

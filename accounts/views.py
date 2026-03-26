import smtplib
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from Proppi import settings
from accounts.utils import es_comercio
from .forms import CustomUserCreationForm, UserUpdateForm
from django.contrib.auth import login, logout, update_session_auth_hash
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
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout
from .models import Empleado, Propietario
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from .utils import es_comercio, es_empleado
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def crearcc(request):
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "accounts/crearcuenta.html", {"form": form})
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): #Si formulario enviado por el POST es valida
            try:
                with transaction.atomic(): #Asegura que la creación del usuario y el propietario se realicen como una sola transacción
                    user = form.save(commit=False)
                    user.is_active = False #Desactivar cuenta hasta que se confirme el correo
                    user.save()
                    Propietario.objects.create(user=user) #Crear un propietario asociado al usuario

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


def signin(request):
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 semanas en segundos
                else:
                    request.session.set_expiry(0)  # Expira al cerrar el navegador
                login(request, user)# Redirigimos al inicio y que el base.html decida qué mostrar
                return redirect('inicio')
            else:
                return render(request, 'accounts/login.html', {
                    'form': AuthenticationForm(),
                    'error': 'Tu cuenta aún no ha sido activada. Revisá tu email.'
                })
        else:
            return render(request, 'accounts/login.html', {
                'form': AuthenticationForm(),
                'error': 'Usuario y/o contraseña son incorrectos'
            })

@login_required
def signout(request):
     logout(request)
     return redirect('inicio')

#Vista para el perfil
@login_required
def ver_perfil(request):
    user = request.user
    return render (request, 'accounts/perfil.html', {'user': user})
    
@login_required
@user_passes_test(es_comercio, login_url='inicio')
def editar_perfil_propietario(request):
    user = request.user
    form = UserUpdateForm(instance=user)
    if request.method == 'GET':
        return render(request, 'accounts/editar_perfil.html', {'user': user, 'form': form})
            
@login_required
@user_passes_test(es_empleado, login_url='inicio')
def editar_perfil_empleado(request):
    user = request.user
    form = UserUpdateForm(instance=user)
    if request.method == 'POST':
        nuevo_alias = request.POST.get('alias')
        if not Empleado.objects.filter(alias=nuevo_alias).exclude(id=user.empleado.id).exists():
            empleado = user.empleado
            empleado.alias = nuevo_alias
            empleado.save()
            messages.success(request, 'Alias actualizado exitosamente.')
            return redirect('ver_perfil')
        else:
            messages.error(request, 'El alias ya está en uso. Por favor elige otro.')
            
    return render(request, 'accounts/editar_perfil.html', {'user': user, 'form': form})


@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)  # Evita que el usuario sea desconectado después de cambiar la contraseña
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('ver_perfil')
        else:
            messages.error(request, 'Por favor corrige los errores indicados')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/cambiar_contrasena.html', {'form': form})

def olvidar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            try:
                enviar_email_restablecer_contrasena(request, user)
                messages.success(request, 'Se ha enviado un email con instrucciones para restablecer tu contraseña.')
                return redirect('login')
            except Exception as e:
                print({e})
                messages.error(request, 'Error al enviar el email')
        except User.DoesNotExist:
            messages.error(request, 'Si el email ingresado está registrado, recibirás un mensaje con instrucciones para restablecer tu contraseña.')
            return redirect('olvidar_contrasena')
    return render(request, 'accounts/olvidar_contrasena.html')


def enviar_email_restablecer_contrasena(request, user):
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    current_site = get_current_site(request)
    mail_subject = 'Restablece tu contraseña'
    message = render_to_string('accounts/restablecer_contrasena.html', {
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
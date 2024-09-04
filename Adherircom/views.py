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
from .forms import Def_usuario
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from Cuentamaster.models import *
import logging
from django.db.models import F
from django.contrib.auth.models import Group
from Autotask.tasks import enviacorreo

# Create your views here.
def crearcc(request):
    if request.method == "GET":
        form = Def_usuario()
        return render(request, "crearcuenta.html", {"form": form})
    else:
        form = Def_usuario(request.POST)
        if form.is_valid(): #Si formulario enviado por el POST es valida
            try:
                user = form.save(commit=False)
                user.is_active = False #Desactivar cuenta hasta que se confirme el correo
                user.save()
                user_profile = UserProfile.objects.create(
                    user=user,
                    cuit=form.cleaned_data['cuit']
                )                    
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
        cuenta = cuentamain.objects.get(id=1)
        cuenta.add_totusuarios()

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
        if form.is_valid():
            comercio_data = form.cleaned_data
            request.session['comercio_data'] = comercio_data
            return redirect(regemp)
        else:
            return render(request, 'regcomercio.html',{
            'form' : Registrocomercio()
             })                

logger = logging.getLogger(__name__)
@login_required
@permission_required("Adherircom.add_comercio")
def regemp(request):
    if request.method == 'GET':
        return render(request, 'regempleado.html', {
            'form': Registroempleado(),
            'horario_form': HorarioTrabajoForm(),
        })        
    else:
        action = request.POST.get('action')
        if action == 'guardar':
                comercio_data = request.session.get('comercio_data')
                if comercio_data:
                    try:
                        with transaction.atomic():
                            comercio_obj = Comercio.objects.create(user=request.user, **comercio_data)  # Asigna el usuario aquí
                            asignaqr(comercio_obj, request)
                            asignaqr_entrada(comercio_obj, request)
                            comercio_obj.save()
                            cant_empleados = 0
                            correo_empleados = []
                            empleados = request.session.get('empleados', [])
                            for empleado_data in empleados:
                                cant_empleados +=1

                                clave_unica = generar_clave_aleatoria()
                                user_empleado = crea_user_empleado(empleado_data, clave_unica)

                                empleado_obj = Empleado.objects.create(
                                    nombre=empleado_data['nombre'],
                                    email=empleado_data['email'],
                                    alias=empleado_data['alias'],
                                    cuil=empleado_data['cuil'], 
                                    user = user_empleado
                                )

                                #Se asigna el empleado al comercio debido al cmapo manytomany
                                empleado_obj.comercios.add(comercio_obj)

                                for horario in empleado_data['horarios']:
                                    HorarioTrabajo.objects.create(
                                        empleado=empleado_obj,
                                        dia_semana=horario['dia_semana'],
                                        cantidad_horas=horario['cantidad_horas']
                                    )

                                correo_empleados.append({
                                    'nombre': empleado_obj.nombre,
                                    'email': empleado_obj.email,
                                    'clave_unica': clave_unica,
                                })                        
                                #Hacer envio de correos con celery
                                enviacorreo.delay(correo_empleados)
                            
                            cuenta_main = cuentamain.objects.get(id=1)  ##Actualizar stats de cuentamain
                            cuenta_main.add_totalempleados(cant_empleados)
                            cuenta_main.add_totalcomercios()
                            

                            del request.session['comercio_data']
                            del request.session['empleados']
                            
                            return redirect('mis_comercios')
                    except IntegrityError as e:
                        logger.error(f"Error al guardar los datos: {str(e)}")
                        return render(request, 'regempleado.html', {
                            'form': form,
                            'horario_form': horario_form,
                            'message': 'Error: Se ha producido un problema al guardar los datos. Por favor, inténtelo de nuevo.'
                        })
        elif action == 'agregar_otro':
            form = Registroempleado(request.POST)
            horario_form = HorarioTrabajoForm(request.POST)
            
            if form.is_valid() and horario_form.is_valid():
                empleados = request.session.get('empleados', [])
                empleado_data = form.cleaned_data
                
                
                if any(emp['cuil'] == empleado_data['cuil'] for emp in empleados):
                    return render(request, 'regempleado.html', {
                        'form': form,
                        'horario_form': horario_form,
                        'message': 'El CUIL ya existe en la lista de empleados agregados.'
                    })

                horarios = []
                for i in range(0, 7):
                    if horario_form.cleaned_data.get(f'dia_{i}'):
                        cantidad_horas = horario_form.cleaned_data.get(f'cantidad_horas_{i}')
                        if cantidad_horas is not None:
                            horarios.append({
                                'dia_semana': i,
                                'cantidad_horas':float (cantidad_horas)
                            })
                empleado_data['horarios'] = horarios
                empleados.append(empleado_data)                 #Pone al empleado al final de la lista
                request.session['empleados'] = empleados        #Se agrega a la lista de empleados de la sesión
                
                print(action)
                print("Empleado agregado")

                return render(request, 'regempleado.html', {
                    'form': Registroempleado(),
                    'horario_form': HorarioTrabajoForm(),
                    'success_message': 'Empleado agregado. Agrega otro o guarda todo.'
                })
            else:
                print("Empleado no agregado")
                return render(request, 'regempleado.html', {
                    'form': form,
                    'horario_form': horario_form,
                    'form_error': form.errors,
                    'horario_form_error': horario_form.errors,
                })
        

def crea_user_empleado(empleado_data, clave_unica):
    user = User.objects.create_user(
        username = empleado_data['cuil'],
        password = clave_unica,
        first_name = empleado_data['nombre'],
        email = empleado_data['email']
    )
    grupo_usuario_empleado = Group.objects.get(name='usuario-empleado')
    user.groups.add(grupo_usuario_empleado)
    return user
    
@login_required
def asignaqr(dato_comercio, request=HttpResponse()):
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

def generar_clave_aleatoria():
    caracteres = string.ascii_uppercase + string.digits 
    clave = ''.join(random.choice(caracteres) for _ in range(5))
    return clave

def signout(request):
     logout(request)
     return redirect('inicio')
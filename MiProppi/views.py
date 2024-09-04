from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from Adherircom.forms import *
from Adherircom.models import *
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, permission_required
from django.core.serializers import serialize
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db import transaction, IntegrityError
from Adherircom.views import generar_clave_aleatoria, enviacorreo, crea_user_empleado
from Cuentamaster.models import *
import logging
from Autotask.tasks import enviacorreo

# Create your views here.


#Vistas usuario-dueño
def signin(request): #Comprobar en base de datos si datos existen  Añadir olvide contraseña
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'login.html', {
        'form' : form
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render(request, 'login.html', {
                'form' : AuthenticationForm,
                'error' : 'Usuario y/o contraseña son incorrectos'
            })
        else: #Verifica que pertenezca al grupo usuario-comercio
            if user.groups.filter(name='usuario-comercio').exists():
                login(request,user)
                return redirect('inicio')
            else:
                return render(request, 'login.html', {
                'form' : AuthenticationForm,
                'error': 'No tienes permisos para acceder como comercio.'
                })
  
@login_required
@permission_required("Adherircom.view_comercio")
def cuenta(request):  #Muestra comercios segun sea usuario-comercio o usuario-empleao
    if request.user.groups.filter(name='usuario-comercio').exists():
        comercios = Comercio.objects.filter(user=request.user)
    elif request.user.groups.filter(name='usuario-empleado').exists():
        empleado = Empleado.objects.filter(user=request.user).first()
        if empleado:
            comercios = Comercio.objects.filter(empleados__in=[empleado])
        else:
            comercios = Comercio.objects.none()
    else:
        comercios = Comercio.objects.none()

    return render(request, 'mis_comercios.html', {
        'comercios': comercios
    })

logger = logging.getLogger(__name__)
@login_required
@permission_required("Adherircom.view_comercio")
def detalle_comercio(request, comercio_id):
    comercio = get_object_or_404(Comercio, id=comercio_id)
    return render(request, 'detalle_comercio.html',{
        'comercio': comercio
    })

@login_required
@permission_required("Adherircom.change_comercio")
def subir_imagen_comercio(request, comercio_id):
    comercio = get_object_or_404(Comercio, id=comercio_id)
    
    if request.method == 'POST':
        imagen = request.FILES.get('imagen')
        if imagen:
            comercio.imagen = imagen
            comercio.save()
            return redirect('detalle_comercio', comercio_id=comercio.id)
    
    return render(request, 'detalle_comercio.html', {'comercio': comercio})

@login_required
@permission_required("Adherircom.add_empleado")
def agregar_emp(request, comercio_id):
    comercio_obj = get_object_or_404(Comercio, id=comercio_id) #Obtener el comercio
    if request.method == 'GET':
        return render(request, 'agregar_emp.html', {
            'comercio': comercio_obj,
            'form': Registroempleado(),
            'horario_form': HorarioTrabajoForm(),
        })
    elif request.method == 'POST':
        form = Registroempleado(request.POST)
        horario_form = HorarioTrabajoForm(request.POST)
        try:
            with transaction.atomic():
                if form.is_valid() and horario_form.is_valid():
                    empleado_data = form.cleaned_data
                    
                    #Procesamiento de horarios
                    horarios=[]
                    for i in range(0, 7):
                        if horario_form.cleaned_data.get(f'dia_{i}'):
                            cantidad_horas = horario_form.cleaned_data.get(f'cantidad_horas_{i}')
                            if cantidad_horas is not None:
                                horarios.append({
                                    'dia_semana': i,
                                    'cantidad_horas':float (cantidad_horas)
                                })
                    empleado_data['horarios'] = horarios

                    clave_unica = generar_clave_aleatoria()
                    user_empleado = crea_user_empleado(empleado_data, clave_unica)

                    #Se crea el objeto empleado sin asignarle un comercio
                    empleado_obj = Empleado.objects.create(
                        nombre=empleado_data['nombre'],
                        email=empleado_data['email'],
                        alias=empleado_data['alias'],
                        cuil=empleado_data['cuil'],
                        user = user_empleado
                    )

                    #Se asigna el empleado al comercio
                    empleado_obj.comercios.add(comercio_obj)

                    for horario in empleado_data['horarios']:
                        HorarioTrabajo.objects.create(
                            empleado=empleado_obj,
                            dia_semana = horario['dia_semana'],
                            cantidad_horas = horario['cantidad_horas']
                        )

                    correo_empleado = []
                    correo_empleado.append({
                        'nombre': empleado_obj.nombre,
                        'email': empleado_obj.email,
                        'clave_unica': clave_unica,
                    })
                    enviacorreo.delay(correo_empleado)

                    cuenta_main = cuentamain.objects.get(id=1)
                    cuenta_main.add_empleado()
                    return redirect('detalle_comercio', comercio_id=comercio_id)   
        except Exception as e:  # Captura la excepción y obtén detalles
            print(f"Error al agregar empleado: {e}")  # Imprime el error para depuración
            return render(request, 'agregar_emp.html', {
                'form': form,
                'horario_form': horario_form,
                'comercio': comercio_obj,
                'message': "No se pudo agregar con éxito al empleado, intente nuevamente"
            })  # Devuelve una respuesta renderizada con el mensaje de error

    return render(request, 'agregar_emp.html', {
        'form': form,
        'horario_form': horario_form,
        'comercio': comercio_obj,
        'message': "No se pudo agregar con éxito al empleado, intente nuevamente"
    })  # Devuelve una respuesta renderizada con el mensaje de error

@login_required
@permission_required("Adherircom.delete_empleado")
def eliminar_emp(request, comercio_id):
    comercio_obj = get_object_or_404(Comercio, id=comercio_id)
    empleados = Empleado.objects.filter(comercios=comercio_obj)

    if request.method == 'GET':
        return render(request, 'eliminar_emp.html', {
            'comercio': comercio_obj,
            'empleados': empleados
        })
    elif request.method == 'POST':
        empleado_id = request.POST.get('empleado_id')
        try: 
            print("busca eliminar")
            if elimina_emp(empleado_id) :
                return render(request, 'eliminar_emp.html', {
                    'comercio': comercio_obj,
                    'empleados': empleados,
                    'message' : "Empleado eliminado con exito"
                 })
            else:
                return render(request, 'eliminar_emp.html', {
                    'comercio': comercio_obj,
                    'empleados': empleados,
                    'message' : "No se pudo eliminar el empleado, intentelo nuevamente"
                 })             
        except:
            return render(request, 'eliminar_emp.html', {
                'comercio': comercio_obj,
                'empleados': empleados,
                'message' : "No se pudo eliminar el empleado, intentalo nuevamente"
            })

def elimina_emp(empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        #Agregar confirmacion de eliminacion
        empleado.delete()
        return True
    except Empleado.DoesNotExist:
        return False
    

#Login  y vistas del empleado. 
#Login es distinto por pertenecer al grupo usuario-empleado

def login_empleado(request):
    if request.method == 'GET':
        return render(request, 'login_empleado.html', {
        'form' : AuthenticationForm
        })
    elif request.method == 'POST':
        user = authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render(request, 'login_empleado.html', {
                'form' : AuthenticationForm,
                'error' : 'Usuario y/o contraseña son incorrectos'
            })
        else: #Verificar que el usuario pertenezca al grupo usuario-empleado
            if user.groups.filter(name='usuario-empleado').exists():
                login(request,user)
                return render(request,'index.html')
            else:
                return render(request, 'login_empleado.html', {
                    'form': AuthenticationForm,
                    'error': 'No tienes permisos para acceder como empleado.'
                })

@login_required
@permission_required("MiProppi.add_checkinout")
def perfil(request):
    empleado = get_object_or_404(Empleado, user=request.user)
    comercios = empleado.comercios.all()
    return render(request, 'perfil.html', {
        'empleado': empleado,
        'comercios': comercios
    })

def checkin(request, comercio_id):  ##Aca se deberá manejar la vista del checkin de los empleados
    comercio = get_object_or_404(Comercio, id=comercio_id)
    if request.method == 'GET':
        return render(request, 'checkin.html',{'comercio': comercio})
    else:
        if request.method =='POST':
            cuil = request.POST.get('cuil')
            if not cuil:
                return render(request, 'checkin.html',{'comercio': comercio})    

        try: #Verifica que el codigo exista
            empleado = Empleado.objects.get(cuil=cuil)
            #Verifica que el empleado pertenezca al comercio
            if not empleado.comercios.filter(id=comercio.id).exists():
                return render(request, 'checkin.html', {'comercio': comercio, 'error': 'No perteneces a este comercio'})
            
            hora_actual = timezone.now()
            dia_semana_actual = hora_actual.weekday()

            #Verifica que tenga día asignado
            try:
                horario = HorarioTrabajo.objects.get(empleado=empleado, dia_semana=dia_semana_actual)
            except HorarioTrabajo.DoesNotExist:
                return render(request, 'checkin.html',{'comercio': comercio, 'error': 'No tienes un horario asignado para hoy'})
           
            #Verificar que empleado no haya hecho el checkin ya
            hoy = timezone.localdate()
            checkin_existente = CheckInOut.objects.filter(empleado=empleado, comercio=comercio, hora_entrada__date=hoy).exists()
            print(checkin_existente)
            if checkin_existente:
                return render(request, 'checkin.html', {'comercio': comercio, 'error': 'Ya has hecho check-in hoy'})
        except Empleado.DoesNotExist:
            return render(request, 'checkin.html',{'comercio': comercio, 'error': 'Código no valido y/o no existe'})

        #Calcular hora de salida
        cantidad_horas = horario.cantidad_horas
        hora_salida = hora_actual + timedelta(hours=float(cantidad_horas))


        CheckInOut.objects.create(
            empleado=empleado,
            comercio=comercio,
            hora_entrada=hora_actual,
            hora_salida=hora_salida,
            completado=True
        )
        
        return JsonResponse({'success': 'Check-in registrado con exito.', 'hora_entrada': hora_actual , 'hora_salida': hora_salida}) #Debe retornar un html

@login_required
@permission_required("MiProppi.add_checkinout")
def configurar_perfil(request): #Corregir excepciones
    empleado = get_object_or_404(Empleado, user=request.user)  # Asumiendo que el modelo Empleado tiene una relación con el User
    if request.method == 'GET':
        form = ConfigurarPerfilForm(instance=empleado)
        return render(request, 'perfil_empleado_config.html', {
            'form': form,
            'empleado': empleado  # Asegúrate de que 'empleado' está incluido en el contexto
        })
    else:
        if request.method == 'POST':
            form = ConfigurarPerfilForm(request.POST, instance=empleado)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cambios realizados con éxito.')
                return redirect('config_empleado')  # Redirige a una página de confirmación o al perfil del usuario
            else:
                print("Errores:", form.errors)

    return render(request, 'perfil_empleado_config.html', {
        'form': form})


#Comunes a ambos usuarios
@login_required
def cambiar_contrasena(request):
    if request.method == 'GET':
        form = PasswordChangeForm(user=request.user)
        return render(request, 'cambiar_contrasena.html',{
            'form': form
        })
    elif request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request,'Contraseña modificada con éxito')
            return redirect('config_empleado')
        else:
            return render(request, 'cambiar_contrasena.html',{
                'form': form
            })

def recuperar_contraseña(request):
    return render(request, 'recuperar_contraseña.html')
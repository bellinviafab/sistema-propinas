from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from Adherircom.models import *
from .models import *
from .forms import *
from Adherircom.views import *
from django.contrib.auth.decorators import login_required, permission_required
from django.core.serializers import serialize
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db import transaction, IntegrityError
import logging
from Autotask.tasks import enviacorreo
from django.http import HttpResponseRedirect
from datetime import date


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

def perfil_usercom_config(request):
    usercom = get_object_or_404(User, id=request.user.id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=usercom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios realizados con éxito.')
            return redirect('perfil_usercom_config')
        else:
            messages.error(request, 'Ocurrió un error al realizar los cambios. Por favor, verifica los campos.')
    else:
        form = UserUpdateForm(instance=usercom)

    return render(request, 'perfil_usercom_config.html',{'form':form})

logger = logging.getLogger(__name__)
@login_required
@permission_required("Adherircom.view_comercio")
def detalle_comercio(request, comercio_id):
    comercio = get_object_or_404(Comercio, id=comercio_id)
    asignacion = TieneAsignado.objects.filter(id_comercio=comercio)
    ingreso_diario = IngresoDiario.objects.filter(
        id_comercio = comercio,
        fecha = date.today()
    )
    print(ingreso_diario)
    return render(request, 'detalle_comercio.html',{
        'comercio': comercio,
        'asignacion': asignacion,
        'ingreso_diario': ingreso_diario,
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
            'user_form': UserEmpleadoForm(),
            'emp_form': EmpleadoForm(),
            'horario_form': HorarioTrabajoForm(),
        })
    else:
        user_form = UserEmpleadoForm(request.POST)
        emp_form = EmpleadoForm(request.POST)
        horario_form = HorarioTrabajoForm(request.POST)

        if user_form.is_valid() and emp_form.is_valid():
            try:
                with transaction.atomic():
                    # Crear el usuario, crear el empleado y asignarselo al user, asignar cada usuario al comercio(fecha de ingreso),
                    #Asignar por cada horario de trabajo al empleado, asignar el user empleado al grupo usuario-empleado, enviar email al empleado

                    user = User.objects.create_user(
                        username = user_form.cleaned_data['username'],
                        password = generar_clave_aleatoria(),
                        first_name = user_form.cleaned_data['first_name'],
                        last_name = user_form.cleaned_data['last_name'],
                        email = user_form.cleaned_data['email']
                    )
                    empleado = Empleado.objects.create(
                        user=user,
                        alias = emp_form.cleaned_data['alias'],
                    )
                    TieneAsignado.objects.create(
                        id_comercio = comercio_obj,
                        id_empleado = empleado,
                        fecha_ingreso = timezone.now()
                    )
                    for i in range(7):
                        if request.POST.get(f'dia_{i}') and request.POST.get(f'cantidad_horas_{i}'):
                            horario = HorarioTrabajo(
                                empleado = empleado,
                                comercio = comercio_obj,
                                dia_semana = i,
                                cantidad_horas = request.POST.get(f'cantidad_horas_{i}'),
                            )
                            horario.save()
                    grupo_usuario_empleado = Group.objects.get(name='usuario-empleado')
                    user.groups.add(grupo_usuario_empleado)
                    ##enviacorreo.delay() Celery
                    messages.success(request, f"{user.first_name} {user.last_name} ha sido registrado correctamente.")
                    return HttpResponseRedirect(request.path_info)
            except IntegrityError:
                return render(request, 'agregar_emp.html', {
                    'comercio': comercio_obj,
                    'user_form': user_form,
                    'emp_form': emp_form,
                    'horario_form': horario_form,
                    'error': "Hay errores en tu formulario, verifica los campos"
                })
        else:
            return render(request, 'agregar_emp.html', {
                'comercio': comercio_obj,
                'user_form': user_form,
                'emp_form': emp_form,
                'horario_form': horario_form,
                'error': "Hay errores en tu formulario, verifica los campos"
            })



def generar_clave_aleatoria():
    caracteres = string.ascii_uppercase + string.digits 
    clave = ''.join(random.choice(caracteres) for _ in range(5))
    return clave

@login_required
@permission_required("Adherircom.delete_empleado")
def eliminar_emp(request, comercio_id):
    comercio_obj = get_object_or_404(Comercio, id=comercio_id)
    empleados = TieneAsignado.objects.filter(id_comercio=comercio_obj)

    if request.method == 'GET':
        return render(request, 'eliminar_emp.html', {
            'comercio': comercio_obj,
            'empleados': empleados
        })
    elif request.method == 'POST':
        empleado_id = request.POST.get('empleado_id')
        try: 
            print("busca eliminar")
            if elimina_empleado_de_comercio(empleado_id) :
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

def elimina_empleado_de_comercio(empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        #Agregar confirmacion de eliminacion
        empleado.delete()
        return True
    except Empleado.DoesNotExist:
        return False
    

#Vistas del empleado. 
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


"""@login_required
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
        'form': form})"""


#Comunes a ambos usuarios
@login_required
def perfil(request):
    context = {}

    if request.user.groups.filter(name='usuario-empleado').exists():
        empleado = get_object_or_404(Empleado, user=request.user)
        context['empleado'] = empleado
        context['is_empleado'] = True
    elif request.user.groups.filter(name='usuario-comercio').exists():
        context['dueno'] = request.user
        context['is_dueno'] = True
    return render(request, 'perfil.html', context )

@login_required
@permission_required("Adherircom.view_comercio")
def cuenta(request):  #Muestra comercios segun sea usuario-comercio o usuario-empleao
    if request.user.groups.filter(name='usuario-comercio').exists():
        comercios = Comercio.objects.filter(propietario_id=request.user)
    elif request.user.groups.filter(name='usuario-empleado').exists():
        empleado = Empleado.objects.filter(user_id=request.user).first()
        if empleado:
            comercios = Comercio.objects.filter(empleados__in=[empleado])
        else:
            comercios = Comercio.objects.none()
    else:
        comercios = Comercio.objects.none()

    return render(request, 'mis_comercios.html', {
        'comercios': comercios
    })


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

##Fuera del MVP##

"""def checkin(request, comercio_id):  ##Aca se deberá manejar la vista del checkin de los empleados
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
  
        return JsonResponse({'success': 'Check-in registrado con exito.', 'hora_entrada': hora_actual , 'hora_salida': hora_salida}) #Debe retornar un html  """


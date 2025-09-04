import smtplib
from celery import shared_task
from django.utils import timezone
from Adherircom.models import *
from MiProppi.models import *
from decimal import Decimal
from django.db.models import Sum
import mercadopago
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
from email.mime.text import MIMEText
""""
@shared_task
def calcular_propinas():
    try:
        ahora = timezone.now()
        fecha_ayer = ahora.date() - timedelta(days=1)
        comercios = Comercio.objects.all()
        for comercio in comercios:

            inicio_dia = timezone.make_aware(datetime.combine(fecha_ayer, datetime.min.time()))
            fin_dia = inicio_dia + timedelta(days=1, seconds=-1)
            #Sumar todas las propinas del comercio en el día
            propinas_totales = obtener_propinas_totales(comercio, inicio_dia, fin_dia)
            if propinas_totales > 0:
                empleados = Empleado.objects.filter(comercios=comercio)
                # Sumar las horas trabajadas por todos los empleados del comercio en el día actual
                total_horas = calcular_tothoras_trabajadas(empleados, comercio, fecha_ayer)        
                if total_horas > 0: #Si el comercio tiene horas registradas significa que al menos 1 empleado hizo el checkin
                    # Calcular las horas trabajadas por el empleado en el día actual
                    for empleado in empleados:
                        horas_trabajadas = calcular_horaspor_empleado(empleado, comercio, fecha_ayer)
                                      
                        print(f"Empleado: {empleado.nombre}")
                        if horas_trabajadas>0: #Calcula la propina para el empleado basado en las horas trabajdas y el total de horas trabajadas por todos
                            horas_trabajadas = Decimal(horas_trabajadas)
                            total_horas= Decimal(total_horas)
                            propina_empleado = propinas_totales * (horas_trabajadas/total_horas)
                            #Porcentaje de la plataforma
                            porcentaje_plataforma = propina_empleado * Decimal('0.0929')
                            distribuye_propina(empleado, propina_empleado, comercio, porcentaje_plataforma)
    except Exception as e:
        print(f"Error al calcular propinas: {str(e)}")
              
    # Luego de actualizar balances, enviar dinero a los alias de cada empleado
    #enviar_dinero()

def obtener_propinas_totales(comercio, inicio_dia, fin_dia):
    return Propina.objects.filter(
        comercio=comercio,
        fecha__range= (inicio_dia, fin_dia),
        pagado = True
    ).aggregate(total_propinas=Sum('monto'))['total_propinas'] or Decimal('0.00')

def calcular_tothoras_trabajadas(empleados, comercio, fecha_hoy):
    total_horas = 0
    for empleado in empleados:
        checkinouts = CheckInOut.objects.filter(
            empleado=empleado,
            comercio=comercio,
            hora_entrada__date=fecha_hoy,
            completado=True
        )
        for checkinout in checkinouts:
            horario = HorarioTrabajo.objects.get(empleado=empleado, dia_semana=checkinout.hora_entrada.weekday())
            total_horas += float(horario.cantidad_horas)
    return total_horas    


def calcular_horaspor_empleado(empleado, comercio, fecha_hoy):
    horas_trabajadas = 0
    checkinouts = CheckInOut.objects.filter(
        empleado=empleado,
        comercio=comercio,
        hora_entrada__date=fecha_hoy,
        completado=True
    )
    for checkinout in checkinouts:
        horario = HorarioTrabajo.objects.get(empleado=empleado, dia_semana=checkinout.hora_entrada.weekday())
        horas_trabajadas += float(horario.cantidad_horas)
    return horas_trabajadas
"""
def distribuye_propina(empleado, propina_empleado, comercio, porcentaje_plataforma):
    empleado.ingresos_diarios += propina_empleado - porcentaje_plataforma
    empleado.ingresos_total += propina_empleado - porcentaje_plataforma
    comercio.ingresos_total += propina_empleado
    comercio.reset_ingresos_diarios()
    with transaction.atomic():
        empleado.save()
        comercio.save()

def enviar_dinero():
    #Obtener todos los empleados que tienen ingresos diarios para transferir
    empleados = Empleado.objects.filter(ingresos_diarios__gt=0)

    access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
    sdk = mercadopago.SDK(access_token)

    for empleado in empleados:

        monto_neto = empleado.ingresos_diarios 

        #Datos de la transferencia
        transfer_data = {
            "amount": float(monto_neto),
            "currency_id": "ARS",
            "receiver_alias": empleado.alias,
            "description": "Pago de ppp" #Pago de propinas
        }

        try:
            #Crear transferencia usando api de mp
            transfer_response = sdk.money_transfer().create(transfer_data)
            transfer = transfer_response["response"]

            if transfer["status"] == "approved":
                print(f"Pago a {empleado.nombre} exitosa")
                #Actualizar balance del empleado y de la cuentamaster
                empleado.ingresos_diarios = Decimal('0.00')
                empleado.save()
            else:
                print(f"Error al pagar a {empleado.nombre}: {transfer['status_detail']}")
        except Exception as e:
            print(f"Excepcion al pagar a {empleado.nombre}: {str(e)}")

#Enviar mails
@shared_task
def enviacorreo(correo_empleados):
        
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    for empleado in correo_empleados:
        nombre_empleado = empleado['nombre']
        destinatario = empleado['email']
        clave_unica = empleado['clave_unica']

        mensaje = MIMEText(f'¡Hola {nombre_empleado}! \n Tu clave de acceso a Proppi es : {clave_unica} \n Con ella puedes acceder a multiples funciones dentro de la plataforma. Por tu seguridad te recomendamos cambiar la clave.')
        mensaje['Subject'] = 'Tu clave de acceso a Proppi'
        mensaje['From'] = 'proppiarg@gmail.com'
        mensaje['To'] = destinatario

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user,smtp_password)
            server.sendmail(smtp_user, destinatario, mensaje.as_string())

                

                                                
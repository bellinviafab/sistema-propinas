from django.http import HttpResponse
from django.shortcuts import get_object_or_404 , render, redirect
from Adherircom.models import Comercio, Propina
from .forms import propinaform
from django.urls import reverse
import mercadopago
from mercadopago import SDK
import json
import hmac, hashlib, binascii, urllib.parse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal


# Create your views here.


access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
sdk = mercadopago.SDK(access_token)


@csrf_exempt
def deposita_propina(request, comercio_id):
    comercio_objeto = get_object_or_404(Comercio, id=comercio_id)
    if (request.method == 'GET'):
        preference_data = {
            "items": [
                {
                    "title": f"Prueba para {comercio_objeto.nombre_comercio}",
                    "quantity": 1,
                    "unit_price": 1.0,  # Puedes poner un valor por defecto aquí o ajustar según tu lógica
                }
            ],
            "back_urls": {
                "success": request.build_absolute_uri(reverse('pago_exitoso')),
                "failure": request.build_absolute_uri(reverse('pago_fallido')),
                "pending": request.build_absolute_uri(reverse('pago_pendiente'))
            },
            "auto_return": "approved",
            "metadata": {
                "comercio_id": comercio_objeto.id,
                "monto": 1.0  # Puedes ajustar esto según tu lógica
            }
        } 
        preference_response = sdk.preference().create(preference_data)
        preference_id = preference_response["response"]["id"]    
        return render(request, 'deposita_propina.html', {
            'comercio': comercio_objeto,
            'form': propinaform(),
            'preference_id': preference_id,  # Pasar el preference_id al template
        })
    if request.method == 'POST':
        form = propinaform(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            monto = float(monto)
            preference_data = {
                "items": [
                    {
                        "title": f"Prueba para {comercio_objeto.nombre_comercio}",
                        "quantity": 1,
                        "unit_price": monto,
                    }
                ],
                "back_urls": {
                    "success": request.build_absolute_uri(reverse('pago_exitoso')),
                    "failure": request.build_absolute_uri(reverse('pago_fallido')),
                    "pending": request.build_absolute_uri(reverse('pago_pendiente'))
                },
                "auto_return": "approved",
                "metadata": {
                    "comercio_id": comercio_objeto.id,
                    "monto": monto
                }
            }
            preference_response = sdk.preference().create(preference_data)
            if preference_response["status"] == 201:
                init_point = preference_response["response"]["init_point"]
                return redirect(init_point)
        else:
            return render(request, 'deposita_propina.html', {
                'comercio': comercio_objeto,
                'form': form,
            })

@csrf_exempt
def pago_exitoso(request): #Agregar webhook
    return render(request, 'pago_exitoso.html')

@csrf_exempt
def pago_fallido(request):
    return render(request, 'pago_fallido.html')

@csrf_exempt
def pago_pendiente(request):
    return render(request, 'pago_pendiente.html')

@csrf_exempt
def valida_firma(request):
    # Obtener el valor de x-signature del header
    x_signature = request.headers.get('x-signature')
    x_request_id = request.headers.get('x-request-id')

    if not x_signature or not x_request_id:
        return False
    
# Obtener los Query params relacionados con la URL de la solicitud
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(request.build_absolute_uri()).query)   

    # Extraer el "data.id" de los Query params
    data_id = query_params.get('data.id', [''])[0]

    # Separar x-signature en partes
    parts = x_signature.split(',')
    # Inicializar variables para almacenar ts y hash
    ts = None
    hash_received = None

    # Iterar sobre los valores para obtener ts y v1
    for part in parts:
        key_value = part.split('=', 1)
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            if key == 'ts':
                ts = value
            elif key == 'v1':
                hash_received = value

    # Verificar que tanto ts como hash_received no estén vacíos
    if not ts or not hash_received:
        return False

    # Obtener la clave secreta para el usuario/aplicación desde el sitio de desarrolladores de Mercado Pago
    secret = settings.MERCADO_PAGO_KEY

    # Generar la cadena manifest
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};" 
    # Crear una firma HMAC definiendo el tipo de hash y la clave como un arreglo de bytes
    hmac_obj = hmac.new(secret.encode(), msg=manifest.encode(), digestmod=hashlib.sha256)
    # Obtener el resultado del hash como una cadena hexadecimal
    firma_esperada = hmac_obj.hexdigest()   
    # Comparar la firma generada con la firma recibida
    return firma_esperada == hash_received

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if valida_firma(request):
                if 'type' in data and data['type'] == 'payment':
                    payment_id = data['data']['id']
                    payment_info = sdk.payment().get(payment_id)

                    if payment_info['response']['status'] == 'approved':
                        comercio_id = payment_info['response']['metadata']['comercio_id']
                        monto = Decimal(payment_info['response']['metadata']['monto'])
                        comercio_objeto = get_object_or_404(Comercio, id=comercio_id)
                        try:
                            comercio_objeto.actualiza_ingresos_diarios(monto)
                            print("Ingresos de comercio actualizado")
                        except Exception as e:
                            print(f"Error al actualizar ingresos del comercio: {str(e)}")
                        try:
                            propina = Propina(comercio=comercio_objeto, monto=monto, pagado=True)
                            propina.save()
                            print("Propina guardada")
                        except Exception as e:
                            print(f"Error al guardar la propina: {str(e)}")
                            return HttpResponse(f"Error al guardar la propina: {str(e)}", status=500)
                    return HttpResponse('Notificación recibida y procesada', status=200)
                else:
                    return HttpResponse('Evento no manejado', status=400)
            else:
                return HttpResponse('Firma no válida', status=400)
        except Exception as e:
            return HttpResponse(f'Error al procesar el webhook: {str(e)}', status=500)
    else:
        return HttpResponse('Método no permitido', status=405)


#Vistas del inicio
def faq(request):
    return render(request, 'faq.html')

def contacto(request):
    return render(request, 'contacto.html')

# Proppi - Gestión y Automatización de Propinas 

Proppi es una plataforma web diseñada para resolver la distribución, trazabilidad y cobro digital de propinas en el sector gastronómico, minimizando la carga operativa de los propietarios y evitando los altos costos de intermediación financiera.

## 🚀 El Problema y la Solución
Actualmente, el cobro de propinas está dividido entre las propinas en efectivo y las propinas enviadas mediante algún medio digital cómo transferencia a la cuenta del banco, o de algún mozo específico, para su posterior reparto de manera manual.

**La solución de Proppi:**
Implementación de una arquitectura de cobro "Direct-to-Merchant" utilizando códigos QR dinámicos y el estándar de **Transferencias 3.0**. El dinero viaja directamente desde la billetera del cliente a la cuenta del comercio, y el sistema automatiza el cálculo de reparto basado en las horas trabajadas por turno. Para el MVP proppi está pensando para facilitar el reparto de propinas entre empleados, para futuras versiones está pensado para que Proppi pueda realizar transferencias automaticas masivas a los distintos empleados.

## 🏗️ Arquitectura de Software
El proyecto está construido bajo una arquitectura de Monolito Modular en Django, separando los dominios de negocio para garantizar escalabilidad:

* **`businesses`**: Gestión de locales comerciales, sucursales, configuración de pasarelas de pago y generación automática de QRs (Deep Linking).
* **`staff`**: Control de turnos, empleados y validación de horas trabajadas (Fricción cero para el empleado).
* **`payments`**: Motor de transacciones, procesamiento de Webhooks y cálculo del algoritmo de reparto de propinas.
* **`accounts`**: Gestión de autenticación extendida y perfiles de usuario.

## ⚙️ Stack Tecnológico
* **Backend:** Python, Django, Django REST Framework.
* **Base de Datos:** MySQL.
* **Integraciones:** Mercado Pago (OAuth 2.0 y Webhooks).


## 🛠️ Instalación y Entorno Local

1. Clonar el repositorio:
   `git clone https://github.com/tu-usuario/proppi.git`
2. Crear y activar el entorno virtual:
   `python3 -m venv venv`
   `source venv/bin/activate`
3. Instalar dependencias:
   `pip install -r requirements.txt`
4. Configurar variables de entorno:
   Copiar `.env.example` a `.env` y configurar las credenciales de base de datos y llaves de encriptación.
5. Aplicar migraciones y ejecutar:
   `python manage.py migrate`
   `python manage.py runserver`

## 📊 Diagrama Entidad-Relación y Estructura
DER
<img width="1654" height="1306" alt="proppidb" src="https://github.com/user-attachments/assets/ddc182ee-3269-4fca-9beb-fde590488c07" />


Diagrama de paquetes
<img width="1019" height="811" alt="P-pp drawio" src="https://github.com/user-attachments/assets/d98ab061-f958-48f4-b6ad-b648a7d8364b" />















----------------



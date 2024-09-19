Descripción del proyecto:
-------------------------------------------------------------------------------------------------------------------------------------------
Proppi es una plataforma web diseñada para automatizar la gestión de propinas en restaurantes, cafés y bares. El usuario-comercio se registra en la plataforma, donde puede registrar su comercio y añadir a sus empleados, proporcionando información como nombre, email, alias, días y horas de trabajo. Posteriormente, se genera un código QR específico para cada comercio registrado. Los clientes del comercio pueden escanear este QR para enviar propinas a través de los diferentes métodos de pago que la plataforma ofrece.

A la medianoche de cada día, el sistema calcula y distribuye automáticamente las propinas a los alias de los usuarios-empleados, informándoles por correo electrónico sobre la cantidad de propinas recibidas durante el día, así como el total acumulado.

Finalmente, tanto el usuario-comercio como el usuario-empleado pueden acceder a la plataforma (en el caso del usuario-empleado, su cuenta es creada automáticamente cuando el usuario-comercio los registra) para utilizar diversas funcionalidades y realizar consultas, las cuales se explicarán en detalle más adelante.

------------------------------------------------
Requisitos: (Lista completa en el proyecto)
----------------------------------------------------------------------------------------------------------------------------------------
Antes de ejecutar el proyecto, asegurarse de tener instalar las siguientes dependencias:

    -Python: (Ultima versión estable)
    
    -Django: 5.0.4 (Ultima versión)
    
    -celery: 5.4.0
    
    -asgiref: 3.8.1
    
    -celery: 5.4.0
    
    -django-celery-beat: 2.6.0
    
    -django-redis: 5.4.0
    
    -python-decouple
    
    -python-dotenv
    
    -redis
    
    -mercadopago
    
    -qrcode
    
    -whitenoise
-----------------------------------------------------------------------------------------
Intrucciones de instalación en entorno local:
-----------------------------------------------

1-Clonar repositorio


2-Configurar el entorno virtual utilizando:

      python3 -m venv venv
    
      
      source venv/bin/activate

3- Instalar dependencias:

    pip install -r requirements.txt

4-Configurar variables de entorno:

    -Crear archivo .env en la raiz, añadir variables de entorno para las keys

5-Instalar PostgreSQL


6- Aplicar migraciones


7- Crear superuser 

--------------------------------------------------------------------------------

DER:
------------------------------------------------
![imagen_2024-09-04_123906290](https://github.com/user-attachments/assets/c1eb086a-4d7d-4aba-bda8-82e81c07ec5d)

----------------------------------------------------------------

Estructura del Proyecto:
------------------------------------------------------------------

El proyecto consta de 5 apps principales; (Adherircom, Autotask, Cuentamaster, Inicio, MiProppi):
"Adherircom", "Inicio", "MiProppi" son apps que estan directamente relacionadas con el funcionamiento de la plataforma

"Autotask", "Cuentamaster" son apps para cuestiones internas del sistema (Automatización y actualización de balances)


    "Adherircom":
        




    Cuestiones a agregar:
      -Actualizar cantidad de comercios y cantidad de usuarios registrados H 
      -Más opciones de reparto de propina 
      -Mejorar tema de redireccion de rutas protegidas H
      -Corregir, que botón guardar funcione como un guardar todo H 
      -Si ya esta registrado, que rediriga a la cuenta H 
      -Si ya esta logeado que no figure el log H
      -Cada empleado debería poder estar relacionado con multiples comercios H
    
      -Si empleado es eliminado de un comercio, que lo desligue pero que no borre su cuenta H
    
    
      -Si empleado ya existe en la bd, que pueda ser reutilizado.
    
      -Ocultar public keys
        -Solicitud del front para acceder a las keys

    

    Cosas por terminar:
        -Cambiar base de datos H
        -Hacer prueba con mercado pago en produccion
        -Implementar modo
        -Revisar INFO PARA CUENTA MAIN  
        -Poder ver horarios de cada empleado / poder modificarlos


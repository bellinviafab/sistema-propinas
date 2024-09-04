#Proppi/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proppi.settings')

celery_app = Celery('Proppi')

# Usa una cadena para importar el archivo de configuración del Celery.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas de todos los paquetes Django configurados.
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'calcular-propinas-diarias':{
        'task': 'Autotask.tasks.calcular_propinas',
        'schedule': crontab(minute=0, hour=0),
    }
}
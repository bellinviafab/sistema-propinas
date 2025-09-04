from django.core.management.base import BaseCommand
import requests
from Adherircom.models import Provincia, Ciudad  # Ajustá según tu modelo y app

from django.core.management.base import BaseCommand
import requests
from Adherircom.models import Provincia, Ciudad  # Ajustá si tenés otro nombre

class Command(BaseCommand):
    help = 'Importa provincias y departamentos como ciudades'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Borrando ciudades existentes...")
        Ciudad.objects.all().delete()

        self.stdout.write("🌎 Importando provincias...")
        provincias = requests.get("https://apis.datos.gob.ar/georef/api/provincias?campos=id,nombre").json()["provincias"]
        for p in provincias:
            Provincia.objects.get_or_create(id=p["id"], nombre=p["nombre"])
        self.stdout.write(self.style.SUCCESS("✅ Provincias importadas"))

        self.stdout.write("🏙️ Importando departamentos como ciudades...")
        departamentos = requests.get("https://infra.datos.gob.ar/georef/departamentos.json").json()["departamentos"]
        count = 0
        for d in departamentos:
            nombre = d["nombre"]
            prov_id = d["provincia"]["id"]
            provincia = Provincia.objects.get(id=prov_id)
            Ciudad.objects.get_or_create(nombre=nombre, provincia=provincia)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"🎉 Ciudades importadas correctamente: {count}"))

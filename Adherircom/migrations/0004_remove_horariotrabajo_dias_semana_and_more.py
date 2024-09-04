from django.db import migrations, models
import django.db.models.deletion

def set_default_dia(apps, schema_editor):
    DiaSemana = apps.get_model('Adherircom', 'DiaSemana')
    default_dia, created = DiaSemana.objects.get_or_create(dia='lunes')  # Suponiendo que 'lunes' existe
    HorarioTrabajo = apps.get_model('Adherircom', 'HorarioTrabajo')
    HorarioTrabajo.objects.update(dias_semana=default_dia.id)

class Migration(migrations.Migration):

    dependencies = [
        ('Adherircom', '0003_diasemana_horariotrabajo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='horariotrabajo',
            name='dias_semana',
        ),
        migrations.AlterField(
            model_name='horariotrabajo',
            name='empleado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios_empleado', to='Adherircom.empleado'),
        ),
        migrations.AddField(
            model_name='horariotrabajo',
            name='dias_semana',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='Adherircom.diasemana'),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_dia),
    ]


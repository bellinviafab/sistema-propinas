from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TimeInput, inlineformset_factory
from .models import *



    


class Registrocomercio(ModelForm):
    class Meta:
        model = Comercio
        fields = ['nombre_comercio', 'tipo_comercio', 'nombre_calle', 'numero_calle', 'ciudad']


    def clean(self):
        cleaned_data = super().clean()
        nombre_comercio = cleaned_data.get('nombre_comercio', '')
        nombre_calle = cleaned_data.get('nombre_calle', '')
        numero_calle = cleaned_data.get('numero_calle', '')
        ciudad = cleaned_data.get('ciudad', '').id

        if not nombre_comercio:
            self.add_error('nombre_comercio', 'Este campo es obligatorio.')
        if not nombre_calle:
            self.add_error('nombre_calle', 'Este campo es obligatorio.')
        if not numero_calle:
            self.add_error('numero_calle', 'Este campo es obligatorio.')
        if not ciudad:
            self.add_error('ciudad', 'Este campo es obligatorio.')

        
        # Validar que no exista un comercio con el mismo nombre, calle y número
        if nombre_comercio and nombre_calle and numero_calle:
            existe = Comercio.objects.filter(
                nombre_comercio__iexact=nombre_comercio,
                nombre_calle__iexact=nombre_calle,
                numero_calle=numero_calle
            ).exists()
            if existe:
                raise forms.ValidationError(
                    'Ya existe un comercio con ese nombre en la misma calle y número.'
                )

        return cleaned_data
    



""""

class Registroempleado(ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre','email','alias','cuil']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'cuil': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cuil(self):
        cuil = self.cleaned_data.get('cuil','').strip()

        if not cuil.isdigit():
            raise ValidationError('El CUIL debe contener solo números.')
        
        if len(cuil) != 11:
            raise ValidationError('El CUIL debe contener exactamente 11 digitos')
        
        return cuil


class HorarioTrabajoForm(forms.Form):
    dias = [
        ('dia_0', 'Lunes', 'cantidad_horas_0'),
        ('dia_1', 'Martes', 'cantidad_horas_1'),
        ('dia_2', 'Miércoles', 'cantidad_horas_2'),
        ('dia_3', 'Jueves', 'cantidad_horas_3'),
        ('dia_4', 'Viernes', 'cantidad_horas_4'),
        ('dia_5', 'Sábado', 'cantidad_horas_5'),
        ('dia_6', 'Domingo', 'cantidad_horas_6'),
    ]
    
    for dia, label, horas in dias:
        locals()[dia] = forms.BooleanField(required=False, label=label)
        locals()[horas] = forms.DecimalField(
            required=False,
            widget=forms.NumberInput(attrs={'class':'form-control','min':'0','step':'0.5'})
        )

    def clean(self):
        cleaned_data = super().clean()
        dia_seleccionado = False

        for dia,label,horas in self.dias:
            dia_value = cleaned_data.get(dia)
            horas_value = cleaned_data.get(horas)

            if dia_value:
                dia_seleccionado = True
                if horas_value is None or horas_value < 0 or horas_value > 12:
                    raise forms.ValidationError('Debes ingresar un horario valido si seleccionas un día')

        if not dia_seleccionado:
            raise forms.ValidationError('Debes seleccionar al menos un día y asignarle un horario valido')
        
        return cleaned_data"""
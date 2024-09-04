from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TimeInput, inlineformset_factory
from .models import *
from django.contrib.auth.models import User

class Def_usuario(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    cuit = forms.CharField(
        min_length = 11,
        max_length = 11,
        required = True,
        error_messages={
            'min_length': 'El CUIT debe tener exactamente 11 dígitos.',
            'max_length': 'El CUIT debe tener exactamente 11 dígitos.',           
        }
    )  # Campo para el CUIT en el formulario

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cuit'] 

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name'] 
        if not first_name.isalpha():
            raise forms.ValidationError('El nombre no debe contener números ni caracteres especiales.')
        return first_name            
        
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name'] 
        if not last_name.isalpha():
            raise forms.ValidationError('El apellido no debe contener números ni caracteres especiales.')
        return last_name   

    def clean_cuit(self):
        cuit = self.cleaned_data['cuit']
        if not cuit.isdigit():
            raise forms.ValidationError('El CUIT debe contener solo dígitos')
        return cuit

    def save(self, commit=True):
        user = super().save(commit=False)  
        user.first_name = self.cleaned_data['first_name']  # Asignar nombre
        user.last_name = self.cleaned_data['last_name']  # Asignar apellido
        user.email = self.cleaned_data['email']        # Asignar email
        user_profile = UserProfile(user=user, cuit=self.cleaned_data['cuit'])  
        if commit:
            user.save()
            user_profile.save()
        return user



class Registrocomercio(ModelForm):
    class Meta:
        model = Comercio
        fields = ['nombre_comercio','tipo_comercio','direccion','ciudad','provincia']

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
        
        return cleaned_data
from django import forms
from Adherircom.models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class UserEmpleadoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese CUIL") # Validación de CUIL único, se debería dar posibilidad de que se muestre al usuario con ese cuil para agregarlo igualmente al comercio ya que la relaciones N:M
        else:
            if not username.isdigit() or len(username) != 11:
                raise forms.ValidationError("El cuil debe contener 11 dígitos")
            if not username.startswith(('20', '23', '24', '27', '30', '33', '34', '36', '37')):
                raise forms.ValidationError("El cuil debe comenzar con 20, 23, 24, 27, 30, 33, 34, 36 o 37")

        # Si la validación es exitosa, retorna el username
        return username


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [ 'alias' ]


class HorarioTrabajoForm(forms.ModelForm):
    class Meta:
        model = HorarioTrabajo
        fields = ['dia_semana', 'cantidad_horas']

    def clean_horario_trabajo(self):
        dia = self.cleaned_data.get('dia_semana')
        horas = self.cleaned_data.get('cantidad_horas')
        if dia and horas:
            if horas < 1 or horas > 24:
                raise forms.ValidationError("La cantidad de horas debe estar entre 1 y 24")
        return self.cleaned_data
    


         
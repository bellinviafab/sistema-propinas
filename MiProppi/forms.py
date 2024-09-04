from django import forms
from Adherircom.models import Empleado
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class ConfigurarPerfilForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['email', 'alias']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresa tu nuevo correo'}),
            'alias': forms.TextInput(attrs={'placeholder': 'Ingresa tu nuevo alias'}),
        }



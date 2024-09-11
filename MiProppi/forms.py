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


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
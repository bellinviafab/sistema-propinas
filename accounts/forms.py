from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, TimeInput, inlineformset_factory
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')
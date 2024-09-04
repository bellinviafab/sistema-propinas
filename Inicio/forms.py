from django import forms

class propinaform(forms.Form):
    monto = forms.DecimalField(label='Propina', max_digits=10 , decimal_places=2)
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto<=0:
            raise forms.ValidationError('La propina debe ser un numero mayor que cero y no puede contener caracteres especiales')
        return monto
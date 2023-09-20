from django.forms import ModelForm
from .models import Coupon
from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'


class CouponForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = ''    
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
            'expire_date': DateInput(),
        }
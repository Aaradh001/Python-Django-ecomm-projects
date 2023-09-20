from django import forms
from .models import Order
    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_note']
    
class ChangeOrderStatusForm(forms.ModelForm):

   class Meta:
         model = Order
         fields = ['order_status']
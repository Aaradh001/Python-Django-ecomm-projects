from django import forms
from store.models import Product
# from django.contrib.auth import get_user_model


class ProductCreationForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = [
                'product_name',
                'brand',
                'description',
                'price',
                'images',
                'stock',
                'is_available',
                'category',
                ]
        
        widgets = {
            'product_name': forms.TextInput(attrs = {'class': 'form-control'}),
            'brand': forms.TextInput(attrs = {'class': 'form-control'}),
            'description': forms.TextInput(attrs = {'class': 'form-control'}),
            'price': forms.TextInput(attrs = {'class': 'form-control'}),
            'stock': forms.TextInput(attrs = {'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs = {'class': 'form-check-input'}),
            'images': forms.FileInput(attrs = {'class': 'form-control'}),
            'category': forms.Select(attrs = {'class': 'form-control'}),
            }
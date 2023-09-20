from django import forms
from category_management import models

Category = models.Category

class CategoryForm(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = [
            'category_name',
            'parent',
            'is_valid',
            ]
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'is_valid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }

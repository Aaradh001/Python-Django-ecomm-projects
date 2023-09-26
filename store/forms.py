from django import forms
from store.models import Product, ProductVariant, Brand, Attribute, AttributeValue
# from django.contrib.auth import get_user_model



# Form for adding and editing product 

class ProductForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_available'].widget.attrs['class'] = 'form-check-input'
        
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['prod_slug',]
        


class ProductVariantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['is_active'].widget.attrs['class'] = ''
        

    class Meta:
        model = ProductVariant
        fields = '__all__'
        exclude = ['product','thumbnail_image', 'product_variant_slug','additional_images']


class BrandForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = Brand
        fields = '__all__'
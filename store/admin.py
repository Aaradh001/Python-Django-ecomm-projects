from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, Attribute, AttributeValue, Brand
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'prod_slug': ('product_name',)}
    

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(Attribute)
admin.site.register(AttributeValue)

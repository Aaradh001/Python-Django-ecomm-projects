from django.contrib import admin
from .models import Product,ProductImage
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'prod_slug': ('product_name',)}
    

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)

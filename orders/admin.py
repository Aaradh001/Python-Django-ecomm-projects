from django.contrib import admin
from .models import Order, OrderProduct, PaymentMethod, Payment, Invoice

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(PaymentMethod)
admin.site.register(Payment)
admin.site.register(Invoice)
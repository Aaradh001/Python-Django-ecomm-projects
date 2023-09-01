from django.db import models
from accounts.models import Account, AddressBook
from store.models import Product

# Create your models here.
class PaymentMethod(models.Model):

    method_name     = models.CharField(max_length=100)
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return self.method_name


class Payment(models.Model):
    
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id      = models.CharField(max_length=100)
    payment_method  = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount_paid     = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add = True)
    
    
    def __str__(self):
        return self.payment_id



class Order(models.Model):
    
    ORDER_STATUS_CHOICES = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Delivered", "Delivered"),
        ("Cancelled_Admin", "Cancelled Admin"),
        ("Cancelled_User", "Cancelled User"),
        ("Returned_User", "Returned User"),
        )
    
    user                = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    payment             = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null = True)
    shipping_address    = models.ForeignKey(AddressBook, on_delete=models.SET_NULL,null=True)
    order_number        = models.CharField(max_length=100)
    order_note          = models.CharField(max_length=100, blank=True, null=True)
    order_total         = models.DecimalField(max_digits=12, decimal_places=2)
    tax                 = models.FloatField(null = True)
    order_status        = models.CharField(choices = ORDER_STATUS_CHOICES, max_length=20, default='New')
    ip                  = models.CharField(max_length=50, blank=True)
    is_ordered          = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.order_number


class OrderProduct(models.Model):

    order           = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment         = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null = True)
    user            = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity        = models.IntegerField()
    product_price   = models.DecimalField(max_digits=12, decimal_places=2)
    ordered         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    
    def price_in_order_product(self):
        return self.product_price*self.quantity    
    
    def __str__(self):
        return str(self.order)


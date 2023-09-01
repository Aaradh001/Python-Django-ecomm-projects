from django.db import models
from store.models import Product
from accounts.models import Account
from django.contrib.auth import get_user_model

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length = 150, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    qty = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    
    def subtotal(self):
        return self.product.price * self.qty
    
    
    def __str__(self):
        return str(self.product)
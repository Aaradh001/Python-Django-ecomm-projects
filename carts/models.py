from django.db import models
from store.models import ProductVariant
from accounts.models import Account
from django.contrib.auth import get_user_model
from datetime import datetime
# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length = 150, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    qty = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    
    def subtotal(self):
        
        offer_percentage=0
        # adding catggry offer
        if self.product.product.category.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
                offer_percentage = self.product.product.category.categoryoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).values_list('discount_percentage', flat=True).order_by('-discount_percentage').first()
        
        #adding product offer
        if self.product.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).exists():
                offer_percentage = offer_percentage+self.product.productoffer_set.filter(is_active=True, expire_date__gte=datetime.now()).values_list('discount_percentage', flat=True).order_by('-discount_percentage').first()

        if offer_percentage >=100:
            offer_percentage = 100
            
        offer_price =  self.product.sale_price - self.product.sale_price * (offer_percentage) / (100)
        
        return offer_price * self.qty
    
    
    def __str__(self):
        return str(self.product)
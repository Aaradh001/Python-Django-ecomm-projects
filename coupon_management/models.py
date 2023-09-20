from django.db import models

# Create your models here.
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    discount_percentage = models.IntegerField(default=10)
    minimum_amount = models.IntegerField(default=500)
    description = models.CharField(max_length=100)
    expire_date = models.DateField()
    
    
    
    def save(self, *args, **kwargs):
        if self.discount_percentage > 100:
            self.discount_percentage = 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.coupon_code
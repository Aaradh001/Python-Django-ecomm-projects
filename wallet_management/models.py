from django.db import models
from accounts.models import Account
from orders.models import Order

# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.first_name + str(self.balance)

class WalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES =(
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
        )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    transaction_type = models.CharField(choices = TRANSACTION_TYPE_CHOICES, max_length=10)
    transaction_detail = models.CharField(max_length = 50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.transaction_type + str(self.wallet) + str(self.amount)

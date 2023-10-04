from django.shortcuts import render
import json
from django.http import JsonResponse
from .models import Wallet
from orders.models import Order

# Create your views here.

def get_wallet_grand_total(request):
    
    order_number = request.GET.get('order_number')
    check = request.GET.get('check')
    if order_number:
        
        wallet = Wallet.objects.get(user=request.user,is_active=True)
        order = Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
        payable_total = order.order_total + order.tax
        wallet_balance = wallet.balance  
        
        if check=='true':  
            if wallet.balance <= payable_total  :  
                payable_total = payable_total- wallet.balance   
                wallet_balance = 0
            else:
                wallet_balance = wallet.balance - payable_total
                payable_total = 0
                print(payable_total)
                    
            return JsonResponse({"status": "success", "payable_total": payable_total, "wallet_balance": wallet_balance})
        else:
            return JsonResponse({"status": "success", "payable_total": payable_total, "wallet_balance": wallet_balance})
            
    
from django.shortcuts import render
from carts.models import CartItem
from .models import Coupon
from orders.models import Order
from django.http import JsonResponse
from datetime import date
import json
def coupon_verify(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        current_user = request.user
        data = json.load(request)
        coupon_code = data.get('coupon_code')
        order_number = data.get('order_number')
        
        # Update the order status based on the order_number and selected_option
        coupon = Coupon.objects.filter(coupon_code__iexact=coupon_code,is_active=True,expire_date__gt=date.today())
        if not coupon.exists():
            return JsonResponse({"status": "error", "message": "Invalid Coupon Or Coupon Expired"})
        
        order_total = 0
        tax = 0
        cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        for cart_item in cart_items:
            order_total += cart_item.subtotal()
            
        tax = (5*order_total)/100
        
        if coupon[0].minimum_amount > order_total:
            return JsonResponse({"status": "error", "message": "Minimum Purchase amount "+str(coupon[0].minimum_amount)})
        
        order = Order.objects.get(user = current_user, is_ordered=False, order_number=order_number)
        coupon_discount = (order_total * coupon[0].discount_percentage)/100
        order.order_total = order_total + tax - coupon_discount
        order.coupon_code = coupon[0]
        order.additional_discount = coupon_discount
        grand_total = order.order_total
        order.save()
        
        return JsonResponse({"status": "success",
                             "message": "Coupon Applied "+str(coupon[0].discount_percentage)+"% Discount",
                             "coupon_code": coupon[0].coupon_code,
                             'coupon_discount': coupon_discount,
                             "grand_total": grand_total,
                             "discount_percentage": coupon[0].discount_percentage})

    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})

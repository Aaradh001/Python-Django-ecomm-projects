from django.shortcuts import render,redirect,reverse
from carts.models import CartItem
from .forms import OrderForm,ChangeOrderStatusForm
from .models import Order,OrderProduct,PaymentMethod
from store.models import Product
from django.http import JsonResponse
import json
from django.contrib import messages
from accounts.models import AddressBook
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date
import datetime


# Create your views here.
@login_required(login_url='signin')
def order_summary(request):
    current_user = request.user
    
    #if cart count <=0 
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count= cart_items.count()
    if cart_count <=0:
        return redirect('cart')
    
    grand_total = 0
    total = 0
    tax = 0
    
    for cart_item in cart_items:
        total += cart_item.subtotal()
    
    tax = (5*total)/100
    grand_total = total + tax
   
    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        
        if selected_address_id is None:
            messages.error(request, "Please choose an address")
            return redirect('checkout')
        
        form = OrderForm(request.POST)
        if form.is_valid():
            #store in order table
            data = Order()
            data.user = current_user
            
            #shipping address
            try:
                shipping_address = AddressBook.objects.get(id=selected_address_id)
            except AddressBook.DoesNotExist:
                messages.error(request, "Please choose an address")
                return redirect('checkout')
            
            data.shipping_address = shipping_address
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            #generate order number
            current_datetime = datetime.datetime.now()
            current_year = current_datetime.strftime("%Y")
            current_month = current_datetime.strftime("%m")
            current_day = current_datetime.strftime("%d")
            current_hour = current_datetime.strftime("%H")
            current_minute = current_datetime.strftime("%M")
            concatenated_datetime = current_year + current_month + current_day + current_hour + current_minute
            
            order_number = 'ORD'+concatenated_datetime+str(data.id)
            
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            payment_methods = PaymentMethod.objects.filter(is_active=True)
            # window.location.href = `{{success_url}}/?order_id={{order.order_number}}&method=RAZORPAY&payment_id=${response.razorpay_payment_id}&payment_order_id=${response.razorpay_order_id}&payment_sign=${response.razorpay_signature}`
            context = { 
                'order'             :order,
                'cart_items'        :cart_items,
                'grand_total'       :grand_total,
                'total'             :total,
                'tax'               :tax,
                'shipping_address'  :shipping_address,
                'payment_methods'   :payment_methods,
            }
            return render(request, 'orders/order_summary.html', context)
        else:
            messages.error(request, form.errors)
            return redirect('checkout')
    else:
        return redirect('checkout')


@login_required(login_url='signin')
def order_complete(request, order_number):
        if order_number:
            print("the order number is :", order_number)
            
            try:
                order = Order.objects.get(order_number=order_number)
                print("confirmed")
                order.is_ordered = True
                order.save()
                payment_method_id = request.POST.get('payment_option')
                print("--------------------",payment_method_id)
                try:
                    if payment_method_id:
                        payment_method = PaymentMethod.objects.get(id = payment_method_id, is_active = True)
                        print("the payment method is:",payment_method)
                        if payment_method.method_name == 'COD':
                            cart_items = CartItem.objects.filter(user=request.user)
                            print(cart_items)
                            
            
                            for item in cart_items:
                                orderproduct = OrderProduct()
                                orderproduct.order = order
                                orderproduct.user = request.user
                                orderproduct.product = item.product
                                orderproduct.quantity = item.qty
                                orderproduct.product_price = item.product.price
                                orderproduct.ordered = True
                                orderproduct.save()
                                
                                #reduce the quantity of soled produce
                                
                                product = Product.objects.get(id=item.product.id)
                                product.stock -= item.qty
                                product.save()
                            
                            #clear the cart
                            CartItem.objects.filter(user=request.user).delete()
                        
                except Exception as e:
                    print("the exception in cod is :",e)

                ordered_products = OrderProduct.objects.filter(order=order, ordered = True)
                sub_total = 0
                tax = 0
                grand_total = 0
                for i in ordered_products:
                    sub_total += i.product_price * i.quantity
                tax = (5*sub_total)/100
                grand_total = sub_total+tax    
                context = {
                    'order'             : order,
                    'payment_method'    : payment_method,
                    'order_number'      : order_number,
                    'sub_total'         : sub_total,
                    'tax'               : tax,
                    'grand_total'       : grand_total,
                    'ordered_products'  : ordered_products
                }
                print(order.created_at)
                # del request.session['order_number']
                return render(request, 'orders/order_complete.html',context)
            except Exception as e:
                print(e)
                return redirect('checkout')
        else:
            return redirect('checkout')
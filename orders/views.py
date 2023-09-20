from django.shortcuts import render,redirect,reverse
from carts.models import CartItem
from .models import Order,OrderProduct,PaymentMethod, Payment
from store.models import Product
from wallet_management.models import Wallet, WalletTransaction
from django.http import JsonResponse
import json
from django.contrib import messages
from accounts.models import AddressBook
from coupon_management.models import Coupon
from django.contrib.auth.decorators import login_required
from accounts.otp_verification.secure import razor_pay_key_id, razor_pay_secret_key
from datetime import date
import datetime
import razorpay

# Create your views here.
@login_required(login_url='signin')
def order_summary(request):
    current_user = request.user
    
    #if cart count <= 0 
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count= cart_items.count()
    if cart_count <= 0:
        return redirect('product_store')
    order_total = 0
    tax = 0
    grand_total = 0
    
    for cart_item in cart_items:
        order_total += cart_item.subtotal()
    tax = (5 * order_total) / 100
    grand_total = order_total + tax
    
    if request.method == 'POST':
        selected_address_id = request.POST.get('address01')
        
        if selected_address_id is None:
            messages.error(request, "Please choose an address")
            return redirect('checkout')
        
        data = Order()
        #shipping address
        try:
            shipping_address = AddressBook.objects.get(id=selected_address_id)
        except AddressBook.DoesNotExist:
            messages.error(request, "Please choose an address")
            return redirect('checkout')

        data.user = current_user
        data.tax = tax
        data.order_total = grand_total
        data.shipping_address = shipping_address
        data.order_note = request.POST.get('order_note')
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
        
        order_number = 'HH-ORD'+concatenated_datetime+str(data.id)
        data.order_number = order_number
        data.save()
        
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        coupons = Coupon.objects.filter(is_active=True,expire_date__gt=date.today())
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        # window.location.href = `{{success_url}}/?order_id={{order.order_number}}&method=RAZORPAY&payment_id=${response.razorpay_payment_id}&payment_order_id=${response.razorpay_order_id}&payment_sign=${response.razorpay_signature}`
        context = { 
            'order': order,
            'cart_items': cart_items,
            'coupons': coupons,
            'grand_total': grand_total,
            'total': order_total,
            'tax': tax,
            'shipping_address': shipping_address,
            'payment_methods': payment_methods,
            }
        return render(request, 'orders/order_summary.html', context)
    else:
        # need to check again==========================================================================
        messages.error(request, 'Please choose a payment option ')
        return redirect('checkout')
    

@login_required(login_url='signin')
def place_order(request):
    
    current_user = request.user
    if not Order.objects.filter(user = current_user, is_ordered = False).exists():
        return redirect('order_summary')
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('product_store')
    
    order_total = 0
    tax = 0
    
    for cart_item in cart_items:
        order_total += cart_item.subtotal()
        
    tax = (5*order_total)/100
    if request.method == 'POST':
        if request.POST.get('wallet_balance'):
            wallet_selected = int(request.POST.get('wallet_balance'))
        else:
            wallet_selected = request.POST.get('wallet_balance')
            
        order_number = request.POST.get('order_number_order_summary')
        payment_method = request.POST.get('payment_option')
        
        
        if not payment_method:
            messages.error(request, "Please choose a payment option")
            return redirect('order_summary')
        
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        except Exception as e:
            print(e)
            
        
        if wallet_selected == 1:
            wallet = Wallet.objects.get(user=current_user,is_active=True)
            
            if wallet.balance <= order.order_total  : 
                 
                order.order_total = order.order_total - wallet.balance
                order.wallet_discount = wallet.balance
                order.save()
                   
            else:
                order.wallet_discount = order.order_total
                order.order_total = 0
                order.save()
        try:  
            if order.order_total == 0:
                raise Exception
            if payment_method == 'RAZORPAY':
                client = razorpay.Client(auth=(razor_pay_key_id, razor_pay_secret_key))
                payment = client.order.create({'amount':float(order.order_total) * 100,"currency": "INR"})  
            else:
                payment = False 
        except :
            payment = False
        
        success_url = request.build_absolute_uri(reverse('payment-success'))
        failed_url = request.build_absolute_uri(reverse('payment-failed'))

        context = {
            'order': order,
            'cart_items': cart_items,
            'grand_total': order_total + tax,
            'razor_pay_key_id': razor_pay_key_id,
            'razor_pay_secret_key': razor_pay_secret_key,
            'total': order_total,
            'payment': payment,
            'tax': order.tax,
            'shipping_address': order.shipping_address,
            'payment_method': payment_method,
            'success_url': success_url,
            'failed_url': failed_url, #not for COD
            }
        return render(request, 'orders/place_order.html', context)
    else:
        # messages.error(request, "Please choose a payment option")
        return redirect('order_summary')


def payment_success(request):
    payment_method = request.GET.get('method')
    order_id = request.GET.get('order_id')
    try:
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
    except Exception:
        return redirect('user_home')
    
    payment_method_is_active = PaymentMethod.objects.filter(method_name=payment_method,is_active=True).exists()

    if payment_method == 'COD':
        if payment_method_is_active:
            payment_method = PaymentMethod.objects.get(method_name=payment_method)
            
            payment = Payment(
                user = request.user,
                payment_id = 'PID-COD'+order_id,
                payment_order_id = order_id,
                payment_signature = 'Signed',   
                payment_method = payment_method,
                amount_paid = order.order_total,
                payment_status = 'SUCCESS',
                )
            payment.save()
            
            wallet = Wallet.objects.get(user=request.user, is_active=True)
            wallet.balance = wallet.balance - order.wallet_discount
            wallet.save()
            
            wallet_transaction = WalletTransaction.objects.create(
                wallet = wallet,
                transaction_type = 'DEBIT',
                order = order,
                transaction_detail = str(order.order_number),
                amount = order.wallet_discount
                )
            wallet_transaction.save()
        
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            #move cart items to order product table
            cart_items = CartItem.objects.filter(user=request.user)
            
            for item in cart_items:
                
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product.id
                orderproduct.quantity = item.qty
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()
                
                #reduce the quantity of soled produce
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.qty
                product.save()
            
            #clear the cart
            CartItem.objects.filter(user=request.user).delete()
            
            request.session["order_number"] = order_id
            request.session["payment_id"] = 'PID-COD'+order_id
            return redirect('order_complete')
        else:
            messages.error(request, "COD is not currently available")
            return redirect('checkout')
            # return redirect('payment-failed')

    elif payment_method == 'RAZORPAY':
        payment_id = request.GET.get('payment_id')
        payment_order_id = request.GET.get('payment_order_id')
        payment_sign = request.GET.get('payment_sign')
        payment_method = PaymentMethod.objects.get(method_name=payment_method)
        
        if payment_method_is_active:
            payment = Payment(
                user = request.user,
                payment_id = payment_id,
                payment_order_id = payment_order_id,
                payment_signature = payment_sign,   
                payment_method = payment_method,
                amount_paid = order.order_total,
                payment_status = 'SUCCESS',
                )
            payment.save()
            
            wallet = Wallet.objects.get(user = request.user, is_active = True)
            wallet.balance = wallet.balance - order.wallet_discount
            wallet.save()
            
            wallet_transaction = WalletTransaction.objects.create(
                wallet = wallet,
                transaction_type = 'DEBIT',
                order = order,
                transaction_detail = str(order.order_number),
                amount = order.wallet_discount
                )
            wallet_transaction.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()

            #move cart items to order product table
            cart_items = CartItem.objects.filter(user=request.user)
            
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order = order
                orderproduct.user = request.user
                orderproduct.product = item.product
                orderproduct.quantity = item.qty
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()
                
                #reduce the quantity of sold products
                product = Product.objects.get(id=item.product.id)
                product.stock -= item.qty
                product.save()
            
            #clear the cart
            CartItem.objects.filter(user=request.user).delete()
            
            request.session["order_number"] = order_id
            request.session["payment_id"] = payment_id
            return redirect('order_complete')
        else:
            messages.error(request, "Invalid Payment Method Found")
            return redirect('payment-failed')
    
    elif payment_method == 'WALLET':
        payment_method = PaymentMethod.objects.get(method_name=payment_method)

        payment = Payment(
            user = request.user,
            payment_order_id = order_id,
            payment_method = payment_method,
            amount_paid = order.order_total,
            payment_id = 'PID-WLT' + order_id,
            payment_signature = 'Signed',
            payment_status = 'SUCCESS',
        )
        payment.save()
        
        wallet = Wallet.objects.get(user=request.user, is_active=True)
        wallet.balance = wallet.balance - order.wallet_discount
        wallet.save()
        
        wallet_transaction = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = 'DEBIT',
            order = order,
            transaction_detail = str(order.order_number),
            amount = order.wallet_discount
            )
        wallet_transaction.save()
    
        order.payment = payment
        order.is_ordered = True
        order.save()
        
        #move cart items to order product table
        cart_items = CartItem.objects.filter(user = request.user)
        
        for item in cart_items:
            
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product.id
            orderproduct.quantity = item.qty
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()
            
            #reduce the quantity of soled produce
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.qty
            product.save()
        
        #clear the cart
        CartItem.objects.filter(user = request.user).delete()
        
        request.session["order_number"] = order_id
        request.session["payment_id"] = 'PID-WLT'+order_id
        return redirect('order_complete')
        
    else:
        return redirect('user_account')
        
def payment_failed(request):
    context = {
    'method': request.GET.get('method'),
    'error_code': request.GET.get('error_code'),
    'error_description': request.GET.get('error_description'),
    'error_reason': request.GET.get('error_reason'),
    'error_payment_id': request.GET.get('error_payment_id'),
    'error_order_id': request.GET.get('error_order_id')
    }
    return render(request, 'orders/payment_failed.html',context)

        
def order_complete(request):
    try: 
        if(request.session['order_number'] and request.session["payment_id"]):
            order_number = request.session['order_number']  
            payment_id   = request.session['payment_id']
            
            try:
                order = Order.objects.get(order_number=order_number,is_ordered=True)
                wallet = Wallet.objects.get(user = request.user, is_active = True)
                wallet_transaction = WalletTransaction.objects.get(wallet = wallet, order = order)
                ordered_products = OrderProduct.objects.filter(order_id=order.id)
                sub_total = 0
                tax = 0
                
                for i in ordered_products:
                    sub_total += i.product_price * i.quantity
                    
                tax = (5*sub_total)/100
                payment = Payment.objects.get(payment_id=payment_id)
                
                context = {
                    'order': order,
                    'order_number': order_number,
                    'payment': payment,
                    'sub_total': sub_total,
                    'tax': tax,
                    'grand_total': sub_total + tax,
                    'wallet_discount': wallet_transaction.amount,
                    'coupon_discount': order.additional_discount,
                    'net_payable_amount': order.order_total,
                    'ordered_products': ordered_products
                    }
                
                del request.session['order_number']
                del request.session['payment_id']
                return render(request, 'orders/order_complete.html',context)
            except Exception as e:
                print(e)
                return redirect('user_home')
                
    except Exception as e:
        print(e)
        return redirect('user_home')
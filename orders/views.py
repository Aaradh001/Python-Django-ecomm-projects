from django.shortcuts import render,redirect,reverse
from carts.models import CartItem
from .models import Order,OrderProduct,PaymentMethod, Payment, Invoice
from store.models import Product,ProductVariant
from wallet_management.models import Wallet, WalletTransaction
from django.http import JsonResponse
import json
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from accounts.models import AddressBook
from coupon_management.models import Coupon
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date
from django.http import HttpResponse
import datetime
import razorpay
# pdf convertion
from django.template.loader import get_template
from xhtml2pdf import pisa


# Create your views here.
@login_required(login_url='signin')
def order_summary(request):
    current_user = request.user
    
    #if cart count <= 0 
    cart_items = CartItem.objects.filter(user = request.user, is_active =True)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_store')
    

    total_with_orginal_price = 0
    tax = 0
    order_total = 0
    
    for cart_item  in cart_items:
        order_total += cart_item.subtotal()
        # quantity += cart_item.qty
        total_with_orginal_price += cart_item.product.max_price * cart_item.qty
    tax = (5*order_total)/100
    discount = total_with_orginal_price - order_total
    
    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        
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
        data.order_total = order_total
        data.shipping_address = shipping_address
        data.order_note = request.POST.get('order_note')
        data.ip = request.META.get('REMOTE_ADDR')
        
        data.save()
        
        #generate order number
        order_number = 'HH-ORD'+str(round(datetime.datetime.now().timestamp()))+str(data.id)
        data.order_number = order_number
        data.save()
        
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        coupons = Coupon.objects.filter(is_active=True,expire_date__gt=date.today())
        payment_methods = PaymentMethod.objects.filter(is_active=True)
        # window.location.href = `{{success_url}}/?order_id={{order.order_number}}&method=RAZORPAY&payment_id=${response.razorpay_payment_id}&payment_order_id=${response.razorpay_order_id}&payment_sign=${response.razorpay_signature}`
        context = { 
            'order': order,
            'max_total': total_with_orginal_price,
            'cart_items': cart_items,
            'coupons': coupons,
            'grand_total': order_total,
            'payable_total': order_total + tax,
            'total': order_total,
            'tax': tax,
            'discount': discount,
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
        try:
            wallet_selected = int(request.POST.get('wallet_balance'))
        except:
            wallet_selected = 0
            
        order_number = request.POST.get('order_number_order_summary')
        payment_method = request.POST.get('payment_option')
        
        
        if not payment_method:
            messages.error(request, "Please choose a payment option")
            return redirect('order_summary')
        
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        except Exception as e:
            print(e)
            
        print("wallet selected", wallet_selected)
        if wallet_selected == 1:

            wallet = Wallet.objects.get(user=current_user,is_active=True)
            print(wallet.balance)
            print(order.order_total, order.tax, order_total, tax, order.wallet_discount)
            if not order.wallet_discount:
                if wallet.balance <= order_total + tax  : 
                    order.order_total = (order.order_total + order.tax) - wallet.balance
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
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
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
            'grand_total': order.order_total,
            'razor_pay_key_id': settings.RAZORPAY_KEY_ID,
            'razor_pay_secret_key': settings.RAZORPAY_SECRET_KEY,
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
    current_site = get_current_site(request)
    mail_subject = "Thank you for purchasing at us!"
    message = render_to_string('orders/order_confirmation_mail.html',{
        'user': request.user,
        'domain': current_site,
        'order' : order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = 'html'
    send_email.send()




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
                orderproduct.product_price = item.product.product_price()
                orderproduct.ordered = True
                orderproduct.save()
                
                #reduce the quantity of soled produce
                product_variant = ProductVariant.objects.get(id=item.product_id)
                product_variant.stock -= item.qty
                product_variant.save()
            
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
                orderproduct.product_price = item.product.product_price()
                orderproduct.ordered = True
                orderproduct.save()
                
                #reduce the quantity of sold products
                product_variant = ProductVariant.objects.get(id=item.product.id)
                product_variant.stock -= item.qty
                product_variant.save()
            
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
            orderproduct.product_price = item.product.product_price()
            orderproduct.ordered = True
            orderproduct.save()
            
            #reduce the quantity of soled produce
            product_variant = ProductVariant.objects.get(id=item.product_id)
            product_variant.stock -= item.qty
            product_variant.save()
        
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
                
                invoice = Invoice()
                invoice.order = order
                invoice.save()

                context = {
                    'order': order,
                    'order_number': order_number,
                    'payment': payment,
                    'sub_total': sub_total,
                    'tax': tax,
                    'grand_total': sub_total + tax,
                    'wallet_discount': wallet_transaction.amount,
                    'coupon_discount': order.additional_discount,
                    'net_payable_amount': order.order_total+order.tax,
                    'ordered_products': ordered_products,
                    'invoice': invoice
                    }
                
                # del request.session['order_number']
                # del request.session['payment_id']
                return render(request, 'orders/order_complete.html',context)
            except Exception as e:
                print("123456789")
                print(e)
                return redirect('user_home')
                
    except Exception as e:
        print("qwertyuio")
        print(e)
        return redirect('user_home')




def generate_invoice(request, invoice_number):
    try:
        invoice = Invoice.objects.get(invoice_number = invoice_number)
    except:
        messages.warning(request, 'Invoice not generated for this order !')
    
    try:
        order_products = OrderProduct.objects.filter(order = invoice.order)

    except Exception as e:
        print(e)

    sub_total = 0
    
    for i in order_products:
        sub_total += i.product_price * i.quantity

    template_path = 'orders/invoice_pdf.html'
    context = {
        'invoice': invoice,
        'ordered_products': order_products,
        'sub_total': sub_total,
        'payable_amount': invoice.order.order_total + invoice.order.tax,
        'order': invoice.order,
        }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{invoice.invoice_number}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
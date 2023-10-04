from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from accounts.forms import UserRegistrationForm, AddressBookForm, UserProfilePicForm
from django.views.decorators.cache import cache_control
from accounts.models import UserProfile, AddressBook
from django.contrib import messages
import random
from accounts.otp_verification.helper import MessageHandler
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct, Payment
from wallet_management.models import Wallet, WalletTransaction
from carts.views import _cart_id
import requests
# forgot password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.otp_verification.helper import MessageHandler


import json
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
import random


User = get_user_model()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signin(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        raw_email = request.POST.get("email")
        password = request.POST.get("password")

        email = raw_email.lower().strip()

        check_if_user_exists = User.objects.filter(email=email).exists()
        
        if not check_if_user_exists:
            messages.error(request, 'Invalid username')
            return render(request, 'signin.html')
        try:
            user = User.objects.get(email = email)
        except Exception as e:
            print(e)
        is_valid_password = user.check_password(password)
        if not is_valid_password:
            messages.error(request, 'Invalid password')
            return render(request, 'signin.html')
        
        user = authenticate(email = email, password = password)


        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()

                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart = cart)
                    user_cart_items = CartItem.objects.filter(user = user)

                    for cart_item in cart_items:
                        for user_cart_item in user_cart_items:

                            if cart_item.product == user_cart_item.product:
                                cart_item.qty += user_cart_item.qty
                                cart_item.save()
                                user_cart_item.delete()

                        cart_item.user = user
                        cart_item.save()
            except:
                pass
            login(request, user)
            messages.success(request, "You are successfully signed in")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('user_home')
        else:
            messages.error(request, "Account activation pending!\nKindly check your mailbox for account activation mail.")
            return redirect('signin')
        
    return render(request, 'signin.html')


def user_signup(request):
    
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        context = {'form': form}
        
        if not password:
            messages.error(request, 'Password cannot be blank')
            return render(request, 'user_signup.html',context)
        
        if password != confirm_password:
            messages.error(request, "passwords not matching")
            return render(request, 'user_signup.html',context)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            phone_number = '+91' + phone_number
            user = User.objects.create_user(
                first_name = first_name, 
                last_name = last_name,
                email = email,
                phone_number = phone_number,
                password = password,
                )
            
            UserProfile.objects.create(user = user)
            
            current_site = get_current_site(request)
            mail_subject = "You're almost done! Activate your HarmonicHut account now"
            data = {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                }
            message = render_to_string('accounts_templates/account_activation_link.html', data)
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(request, f'Registration successfull! A verification email has been sent to: {email}. Open this email and click the link to activate your account')
            return redirect('signin')

        else:
            context = {
                'form' : form
            }
            return render(request, 'user_signup.html', context)
    else:
        form = UserRegistrationForm()
    return render(request, 'user_signup.html', {'form': form})



def account_activation(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = User._default_manager.get(pk = uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account has beeen activated')
        return redirect('signin')
    else:
        return HttpResponse('This link has been expired. Click <a href="http://127.0.0.1:8000/">Home </a>to go back')









def otp_generation(request):
    
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')

    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        phone_number = '+91'+phone_number
        user = User.objects.get(phone_number = phone_number)
        if not user:
            messages.error(request, "Invalid phone number")
            return redirect('signin')
        profile = UserProfile.objects.get(user = user)
        new_otp = random.randint(100000,999999)
        profile.otp = new_otp
        profile.save()
        
        message_handler = MessageHandler(phone_number, profile.otp)
        message_handler.send_otp_to_phone()
        return redirect('user_enter_otp', profile.uid)
        
    return render(request, 'admin_templates/otp_login.html')


def enter_otp(request, uid):
    
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = UserProfile.objects.get(uid = uid)
        if not (profile.otp == otp):
            messages.error(request, "Incorrect OTP")
            return render(request, 'admin_templates/enter_otp.html')
        
        login(request, profile.user)
        profile.otp = random.randint(100000,999999)
        profile.save()
        return redirect('user_home')
            
    return render(request, 'admin_templates/enter_otp.html')


def signout(request):
    logout(request)
    return redirect('user_home')


@login_required(login_url='signin')
def user_account(request):
    user = User.objects.get(email = request.user.email)
    context = {
        'user' : user,
    }
    return render(request, 'user_account.html', context)


# <---------------Address management----------------->

@login_required(login_url='signin')
def my_address(request):
    current_user = request.user
    address_form = AddressBookForm()
    addresses = AddressBook.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    context = {
        'addresses': addresses,
        'address_form': address_form,
    }
    return render(request, 'myaddresses.html', context)


@login_required(login_url = 'signin')
def add_address(request, source):

    if request.method == 'POST':
        address_form = AddressBookForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit = False)
            address.user = request.user
            address.save()
            if source == 'checkout':
                return redirect('checkout')
            else:
                return redirect('my_address')
        else:
            context = {
                    'address_form': address_form,
                }
            return render(request, 'myaddresses.html', context)
    
@login_required(login_url = 'signin')
def default_address(request, id):
    try:  
        address = AddressBook.objects.get(id=id)
        address.is_default = True
        address.save()
        return redirect('my_address')
    except AddressBook.DoesNotExist:
        return redirect('my_address')
        
@login_required(login_url = 'signin')
def address_delete(request, id):
    try:  
        address = AddressBook.objects.get(id = id)
        address.is_active = False
        address.save()
        return redirect('my_address')
    except AddressBook.DoesNotExist:
        return redirect('my_address')

# <---------------Address management end----------------->

# <---------------Order management user----------------->
@login_required(login_url='signin')
def order_history(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    orders_count = orders.count()
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    
    context = {
        'orders': paged_products,
        }
    return render(request, 'order_history.html', context)


@login_required(login_url = 'signin')
def order_history_detail(request, order_id):
    print("hiiiiiiiiiiiiiii")
    print(order_id)
    try:
        order = Order.objects.get(user=request.user, order_number=order_id)
        order_products = OrderProduct.objects.filter(user=request.user, order=order)
        payment = Payment.objects.get(user=request.user, payment_id=order.payment)
        sub_total = 0
        tax = 0
        grand_total = 0
        
        for i in order_products:
            sub_total += i.product_price * i.quantity
    
        tax = (5 * sub_total) / 100
        grand_total  = sub_total + tax

    except Order.DoesNotExist:
        return redirect('store')
      
    context = {
        'order': order,
        'sub_total': sub_total,
        'tax': tax,
        'grand_total': grand_total,
        'order_products': order_products,
        'payment': payment,
        }
    
    return render(request, 'order_detail.html', context)


# <---------------Cancel order by user----------------->

@login_required(login_url='signin')
def order_cancel_user(request,order_id):
    
    order = Order.objects.get(user=request.user, order_number=order_id)
    if not order.order_status == 'Cancelled by User':
        order.order_status='Cancelled by User'
        order.save()
        wallet = Wallet.objects.get(user=request.user,is_active=True)
        wallet.balance += (order.order_total + order.wallet_discount)
        wallet.save()
        
        wallet_transaction = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = 'CREDIT',
            transaction_detail = str(order.order_number) + '  CANCELLED',
            amount = order.wallet_discount
            )
        wallet_transaction.save()
        
        return redirect('order-history-detail', order_id=order.order_number)
    else:
        return redirect('order-history-detail', order_id=order.order_number)


@login_required(login_url = 'signin')
def order_return_user(request, order_id):
    
    order = Order.objects.get(user=request.user, order_number=order_id)
    if not order.order_status == 'Returned':
        order.order_status = 'Returned'
        order.save()
        wallet = Wallet.objects.get(user=request.user,is_active=True)
        wallet.balance += (order.order_total + order.wallet_discount)
        wallet.save()
        
        wallet_transaction = WalletTransaction.objects.create(
            wallet = wallet,
            transaction_type = 'CREDIT',
            transaction_detail = str(order.order_number) + '  RETURNED',
            amount = order.wallet_discount
            )
        wallet_transaction.save()
        return redirect('order-history-detail', order_id=order.order_number)
    else:
        return redirect('order-history-detail', order_id=order.order_number)
    
















# <----------------Forgot password----------------->
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email__iexact = email)
            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            data = {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
                }
            message = render_to_string('accounts_templates/reset_password_email.html', data)
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            
            messages.success(request, f'Password reset link has been send to {email}')
            return redirect('signin')
        
        else:
            messages.error(request, f"User with email id: {email} doesn't exists!")
            return redirect('forgot_password')
    
    return render(request, 'forgot-password.html')

def resetpassword_validate(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = User._default_manager.get(pk = uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('signin')

    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print(password)
        print(confirm_password)
        
        if password == confirm_password:
            uid = request.session.get('uid')
            print(uid)
            user = User.objects.get(pk = uid)
            print(user)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('signin')
            
        else:
            messages.error(request, 'passwords do not match')
            return redirect('reset_password')
    else:
        return render(request, 'reset-password.html')

# <-----------------Forgot password end------------------->


# <-----------------User-profile------------------->

@login_required(login_url='signin')
def update_profile_picture(request):
    if request.method == 'POST':
        form = UserProfilePicForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_account')  
    else:
        return redirect('user_account')


# UPDATE USER FIELDS - lastname and firstname USING AJAX
@login_required(login_url='signin')
def update_fields_user(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        field = data['field']
        value = data['value']
        
        try:
            user = User.objects.get(id=request.user.id)
            field_mapping = {
                'first_name': 'first_name',
                'last_name': 'last_name',
                }
            if field in field_mapping:
                setattr(user, field_mapping[field], value)
                user.save()
            return JsonResponse({"status": "success"})
        
        except:
            return JsonResponse({"status": "error", "message": "Contact Admin"})

    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})


#change mobile number
@login_required(login_url='signin')
def change_mobile_with_otp(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_mobile = data['new_mobile']
        get_new_mobile = '+91' + get_new_mobile
        
        if (request.user.phone_number == get_new_mobile):
            return JsonResponse({"status": "error", "message": 'Entered mobile is same as current mobile number'})
        
        try:
            user = User.objects.get(phone_number = request.user.phone_number)
            #SEND OTP TO Mobile
            otp = random.randint(1000,9999)
            print(otp)
            user_otp, created = UserProfile.objects.update_or_create(user=user, defaults={'otp': f'{otp}'})
            
            try:
                messagehandler = MessageHandler(get_new_mobile, otp).send_otp_to_phone()
            except Exception as e:
                messages.error(request, "Unable to send OTP contact Harmonichut help center")
                return JsonResponse({"status": "error", "message": 'Unable to send otp , Please check mobile again'})
            
            return JsonResponse({"status": "success", "message": get_new_mobile})
        except:
            return JsonResponse({"status": "error", "message": 'Unable to send OTP , Please check mobile number again'})
            
    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})


# Verify OTP to change mobile number with ajax
@login_required(login_url='signin')
def change_mobile_with_otp_verify(request):  
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_mobile = data['new_mobile']
        get_otp = data['otp']
        
        get_new_mobile = '+91' + get_new_mobile
        
        user = User.objects.get(id=request.user.id)
     
        userOtp = UserProfile.objects.filter(user=user,otp=get_otp).exists()
        
        if userOtp:
            print(get_new_mobile)
            user.phone_number = get_new_mobile
            user.save()
            messages.success(request, "Mobile number changed cuccessfully")
            return JsonResponse({"status": "success", "message": 'OTP OK'})
        else:
            return JsonResponse({"status": "error", "message": 'Invalid OTP'})


#change email adress
@login_required(login_url='signin')
def change_email_with_email(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_email = data['new_email']
        
        if (request.user.email == get_new_email):
            return JsonResponse({"status": "error", "message": 'Entered email is same as current email'})
        
        try:
            user = User.objects.get(email = request.user.email)
            #SEND OTP TO MAIL
            otp=random.randint(1000,9999)
            user_otp,created = UserProfile.objects.update_or_create(user=user, defaults={'otp': f'{otp}'})
            
            current_site = get_current_site(request)
            mail_subject = 'Update your Email address'
            message = render_to_string ('accounts_templates/change_email_with_email_template.html',{
                'user': user,
                'domain': current_site,
                'otp': user_otp.otp,
                })
            to_email = get_new_email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send() 

            return JsonResponse({"status": "success", "message": 'Enter Otp To Change'})
        except:
            return JsonResponse({"status": "error", "message": 'Unable to send mail , Please check mail again'})
            
    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})

@login_required(login_url='signin')
def change_email_with_email_verify(request):  
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        get_new_email = data['new_email']
        get_otp = data['otp']
        
        user = User.objects.get(id=request.user.id)
     
        userOtp = UserProfile.objects.filter(user=user,otp=get_otp).exists()
        
        if userOtp:
            user.email = get_new_email
            user.save()
            messages.success(request, "Email ID changed successfully")
            return JsonResponse({"status": "success", "message": 'OTP OK'})
        else:
            return JsonResponse({"status": "error", "message": 'Invalid Otp'})


#change password with old password
@login_required(login_url='signin')
def change_user_password_with_oldpass(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
                
        try:
            current_password = request.user.password    #user's current password
            current_password_entered = data['old_password']
            password2 = data['password2']

            matchcheck = check_password(current_password_entered, current_password)
            
            if matchcheck:
                user = User.objects.get(id = request.user.id)
                user.set_password(password2)
                user.save()  
                update_session_auth_hash(request, user)

                messages.success(request, "Password Change Successfully")
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error","message": "Invalid Old Password"})
        
        except:
            return JsonResponse({"status": "error", "message": "Contact Admin"})

    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})
 
# <-----------------User-profile end------------------->


@login_required(login_url='signin')
def my_orders(request):
    order = Order.objects.get(user=request.user)
    order_products = OrderProduct.objects.filter(order=order)
    try:
        payment = Payment.objects.filter(payment_id=order.payment)[0]
    except:
        payment = None
    context = {
        'order': order,
        'order_products': order_products,
        'payment': payment,
        }
    return render(request, 'myorders.html', context)




def my_wallet(request):
    wallet = Wallet.objects.get(user=request.user, is_active=True)
    wallet_transactons = WalletTransaction.objects.filter(wallet = wallet)
    context = {
        'wallet': wallet,
        'wallet_transactions': wallet_transactons,
    }
    return render(request, 'accounts_templates/my_wallet.html', context)
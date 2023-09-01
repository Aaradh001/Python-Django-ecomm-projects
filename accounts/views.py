from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.forms import UserRegistrationForm, AddressBookForm
from django.views.decorators.cache import cache_control
from accounts.models import UserProfile, AddressBook
from django.contrib import messages
import random
from accounts.otp_verification.helper import MessageHandler
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests


User = get_user_model()

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    
    return render(request, 'index.html')
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signin(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        raw_email= request.POST.get("email")
        password= request.POST.get("password")

        email = raw_email.lower().strip()

        check_if_user_exists = User.objects.filter(email=email).exists()
        if not check_if_user_exists:
            messages.error(request, 'Invalid username')
            return render(request, 'signin.html')
        user = authenticate(email=email, password=password)
        if user is not None:
            
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                print(is_cart_item_exists)
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
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
                # if newuser.is_staff==1 and newuser.is_superadmin==1:
                #     return redirect('admin-home')
                return redirect('user_home')
            
        else:
            messages.error(request, "Invalid password")
            return redirect('signin')
        
    return render(request, 'signin.html')



def user_signup(request):
    
    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        
        if password != confirm_password:
            messages.error(request, "passwords not matching")
            context = {
                'form': form
            }
            return render(request, 'user_signup.html',context)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            phone_number = '+91' + phone_number
            email = form.cleaned_data['email']
            user = User.objects.create_user(
                                    first_name = first_name, 
                                    last_name = last_name,
                                    email = email,
                                    phone_number = phone_number,
                                    password= password,)
            UserProfile.objects.create(user = user)
            
            return redirect('user_home')
        else:
            context = {
                'form': form
            }
            return render(request, 'user_signup.html',context)
    else:
        form = UserRegistrationForm()
    return render(request, 'user_signup.html', {'form': form})


def otp_generation(request):
    
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')

    if request.user.is_authenticated:
        return redirect('user_home')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        phone_number = '+91'+phone_number
        user = User.objects.get(phone_number=phone_number)
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
def dashboard(request):
    user = User.objects.get(email = request.user.email)
    context = {
        'user' : user,
    }
    return render(request, 'user_dashboard.html', context)


# <---------------Address management----------------->

@login_required(login_url='signin')
def my_address(request):
    current_user = request.user
    address_form = AddressBookForm()
    addresses = AddressBook.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    print(addresses)
    context ={
        'addresses'      : addresses,
        'address_form'   : address_form,
    }
    return render(request, 'myaddresses.html',context)
    

@login_required(login_url='signin')
def add_address(request, source):

    if request.method == 'POST':
        print("hi im working")
        address_form = AddressBookForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            print(address)
            print("===========================")
            print(source)
            if source == 'checkout':
                return redirect('checkout')
            else:
                return redirect('my_address')
        else:
            context ={
                    'address_form':address_form,
                }
            return render(request, 'myaddresses.html',context)
    
    
@login_required(login_url='signin')
def default_address(request, id):
    try:  
        address = AddressBook.objects.get(id=id)
        print(address.name)
        address.is_default = True
        address.save()
        return redirect('my_address')
    except AddressBook.DoesNotExist:
        return redirect('my_address')
    
    
@login_required(login_url='signin')
def address_delete(request,id):
    try:  
        address = AddressBook.objects.get(id=id)
        address.is_active=False
        address.save()
        return redirect('my_address')
    except AddressBook.DoesNotExist:
        return redirect('my_address')
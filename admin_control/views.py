from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse
from accounts.forms import UserRegistrationForm
from category_management.forms import CategoryForm
from category_management.models import Category
from store.forms import ProductCreationForm
# from store import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
import random
from accounts.models import UserProfile
from store.models import Product, ProductImage
from accounts.otp_verification.helper import MessageHandler

from django.http import HttpResponseBadRequest, JsonResponse
import json

# # Create your views here.

User = get_user_model()

#decorator for checking admin or not
def check_isadmin(view_func, redirect_url="admin_signin"):
    
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superadmin:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You need to be logged in as an admin to access this page")
        else:
            messages.error(request, "You need to be logged in as an admin to access this page")

        redirect_url_ = reverse(redirect_url) + '?next=' + request.path
        return redirect(redirect_url_)

    return wrapper


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='admin_signin')
@check_isadmin
def admin_home(request):
    
    categories = Category.objects.all()
    print("ADMIN-HOME")
    return render(request, 'admin_templates/admin_home.html', {'categories': categories})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def user_management(request):
    # if not request.user.is_superuser or not request.user.is_staff:
    #     return redirect('user_home')
    if not ( request.user.is_authenticated and request.user.is_superadmin):
        return redirect('admin_signin')
        
    user = User.objects.all()
    context = {'user': user}
    return render(request, 'admin_templates/user_management.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def user_edit(request, id):  
    
    if not (request.user.is_authenticated and request.user.is_superadmin):
        return redirect('admin_signin')

    user = User.objects.get(id=id)
    form = UserRegistrationForm(instance = user)

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = form.cleaned_data['is_active']
            user.is_superadmin = form.cleaned_data['is_superadmin']
            user.is_staff = form.cleaned_data['is_staff']
            
            form.save()
            
            messages.success(request, "User updated")
            return redirect('user_management')
            
        else:
            messages.error(request, form.errors)
            return render(request, 'admin_templates/edit_user.html', {'form': form, 'id': id})
    context = {'form': form, 'id': id}
    return render(request, 'admin_templates/edit_user.html', context)


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def user_create(request):

    form = UserRegistrationForm()

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
                
        if password != confirm_password:    # <--- checking passwords are matching --->
            messages.error(request, "passwords not matching")
            context = {
                'form': form
            }
            return render(request, 'admin_templates/create_user.html',context)
        
        if form.is_valid():
            first_name          = form.cleaned_data['first_name']
            last_name           = form.cleaned_data['last_name']
            phone_number        = form.cleaned_data['phone_number']
            email               = form.cleaned_data['email']
            is_active           = form.cleaned_data['is_active']
            is_superadmin       = form.cleaned_data['is_superadmin']
            is_staff            = form.cleaned_data['is_staff']
            
            user = User.objects.create(
                first_name          = first_name,
                last_name           = last_name,
                email               = email,
                phone_number        = phone_number,
                password            = password,
                is_active           = is_active,
                is_superadmin       = is_superadmin,
                is_staff            = is_staff
                )
            
            UserProfile.objects.create(user = user)
            # messages.success(request, 'User created')
            return redirect('user_management')    
        else:
            context = {
                'form': form
            }
            return render(request, 'admin_templates/create_user.html',context)
            
    else:
        form = UserRegistrationForm()
        context = {
            'form' : form,
        }
    return render(request, 'admin_templates/create_user.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_signin(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.method == 'POST':
        raw_email   = request.POST.get("email")
        password    = request.POST.get("password")

        email       = raw_email.lower().strip()

        check_if_user_exists = User.objects.filter(email=email).exists()
        if not check_if_user_exists:
            messages.error(request, 'Invalid email')
            return render(request, 'admin_templates/admin_signin.html')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            
            login(request, user)
            newuser = User.objects.get(email = email)
            if newuser.is_staff and newuser.is_superadmin:
                return redirect('admin-home')
            messages.error(request, "Sorry, you don't have admin privilages!")
            
        else:
            messages.error(request, "Invalid password")
            return redirect('admin_signin')
        
    return render(request, 'admin_templates/admin_signin.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_otp_generation(request):
    
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.method == 'POST':
        phone_number        = request.POST.get('phone_number')
        phone_number        = '+91'+phone_number
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            # error messsage here
            messages.error(request, "Invalid phone number")
            return redirect('admin_otp_login')
        profile = UserProfile.objects.get(user = user)
        new_otp = random.randint(100000,999999)
        profile.otp     = new_otp
        profile.save()
        message_handler = MessageHandler(phone_number, profile.otp)
        message_handler.send_otp_to_phone()
        return redirect('enter_otp', profile.uid)
        
    return render(request, 'admin_templates/otp_login.html')


def enter_otp(request, uid):
    
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = UserProfile.objects.get(uid = uid)

        if not (profile.otp == otp):
            messages.error(request, "Incorrect OTP")
            return render(request, 'admin_templates/enter_otp.html')

        if not (profile.user.is_staff and profile.user.is_superadmin):
            messages.error(request, "Sorry, you don't have admin privilages!")
            return render(request, 'admin_templates/enter_otp.html')
        
        login(request, profile.user)
        profile.otp = random.randint(100000, 999999)
        profile.save()
        return redirect('admin-home')
            
    return render(request, 'admin_templates/enter_otp.html')


   
def block_or_unblock(request, id):
    user = User.objects.get(id=id)
    user.is_active = not user.is_active
    user.save()
    user = User.objects.all()
    return redirect('user_management')



def admin_signout(request):
    logout(request)
    return redirect('admin_signin')


# <-------------------------------------product control-------------------------------------->

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def product_listing(request):
    # if not request.user.is_superuser or not request.user.is_staff:
    #     return redirect('user_home')
    if not ( request.user.is_authenticated and request.user.is_superadmin):
        return redirect('admin_signin')
        
    products    = Product.objects.all()
    context     = {'products': products}
    return render(request, 'admin_templates/product_control/product_listing.html', context)


@check_isadmin
def product_control(request, id):
    product = Product.objects.get(id=id)
    product.is_available    = not product.is_available
    product.save()
    return redirect('products')



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def add_product(request):

    form = ProductCreationForm()
    
    if request.method == 'POST':
        form = ProductCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            product_name           = form.cleaned_data['product_name']
            brand                  = form.cleaned_data['brand']
            description            = form.cleaned_data['description']
            price                  = form.cleaned_data['price']
            images                 = form.cleaned_data['images']
            stock                  = form.cleaned_data['stock']
            category               = form.cleaned_data['category']
            is_available           = form.cleaned_data['is_available']
            
            product = Product.objects.create(
                product_name     = product_name,
                brand            = brand,
                description      = description,
                price            = price,
                images           = images,
                stock            = stock,
                category         = category,
                is_available     = is_available
                )
            
            input_images = []
            for i in range(1,5):
                image = request.FILES['add_image'+str(i)]
                if image:
                    input_images.append(image)
            
            image_list = []            
            for i in input_images:
                image_list.append(ProductImage(product = product, image = i))
            
            if image_list:
                ProductImage.objects.bulk_create(image_list)            
                
            messages.success(request, 'Product added')
            return redirect('products')    
        else:
            context = {
                'form': form
            }
            return render(request, 'admin_templates/product_control/product_add.html',context)
            
    else:
        context = {
            'form' : form,
        }
    return render(request, 'admin_templates/product_control/product_add.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def product_update(request, id):

    product      = Product.objects.get(id=id)
    prod_images  = ProductImage.objects.filter(product=product)
    form         = ProductCreationForm(instance = product)

    if request.method == 'POST':
        form = ProductCreationForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product                 = form.save(commit=False)
            product.is_available    = form.cleaned_data['is_available']
            form.save()
            print(product.stock)
            input_images = []
            for i in range(1,5):
                try:
                    image = request.FILES['add_image'+str(i)]
                    image_value = request.POST.get('product-image'+str(i), "")
                    print(image_value)
                    input_images.append([image, image_value])
                except:
                    pass
            
            for i in input_images:
                if i[0]:
                    change_image = ProductImage.objects.get(id = i[1])
                    change_image.image = i[0]
                    change_image.save()
            
            messages.success(request, "Product updated")
            return redirect('products')
            
        else:
            messages.error(request, form.errors)
            print(form.errors)
            return render(request, 'admin_templates/product_control/product_edit.html', {'form': form, 'id': id})
    
    context = {'form'           : form, 
               'id'             : id,
               'range'          : range(5),
               'product'        : product,
               'prod_images'    : prod_images
               }
    return render(request, 'admin_templates/product_control/product_edit.html', context)
    
    
    # <--------------------category management-------------------->
    
 

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def add_category(request):

    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        print(request.POST.get('parent'))
                
        if form.is_valid():
            form.save()
            return redirect('user_management')
        else:
            context = {
                'form': form
            }
            
            return render(request, 'admin_templates/category-control/add_category.html',context)
            
    else:
        form = CategoryForm()
        context = {
            'form' : form,
        }
    return render(request, 'admin_templates/category-control/add_category.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def edit_category(request, cat_slug):
    
    
    category     = Category.objects.get(cat_slug = cat_slug)
    form         = CategoryForm(instance = category)
    
    if request.method == 'POST':    
        form = CategoryForm(request.POST, instance=category)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated")
            return redirect('admin-home')
        else:
            messages.error(request, form.errors)
            return render(request, 'admin_templates/category-control/edit_category.html', {'form': form})

    context = {
        'form' : form
        }
    return render(request, 'admin_templates/category-control/edit_category.html', context)




@check_isadmin
def category_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':    
            data = json.load(request)
            cat_slug = data.get('checkboxValue')
            category =  Category.objects.get(cat_slug = cat_slug)
            category.is_valid    = not category.is_valid
            category.save()
            return JsonResponse({'context': 'ok'})
    
    else:
        return JsonResponse({'context': 'errror'})

# def practice(request):
    
#     if request.method == 'POST':
#         name = request.POST['name']
#         email = request.POST['email']
#         bio = request.POST['bio']
#         print(name)
#         print(email)
#         print(bio)
    
#     return render(request, 'admin_templates/practice.html')
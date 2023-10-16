from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse
from accounts.forms import UserRegistrationForm
from category_management.forms import CategoryForm
from category_management.models import Category
from store.forms import ProductForm, ProductVariantForm, BrandForm, CreateAttributeValueForm, CreateAttributeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
import random
from accounts.models import UserProfile
from wallet_management.models import Wallet
from store.models import Product, ProductVariant, ProductImage, Attribute, AttributeValue, Brand
from accounts.otp_verification.helper import MessageHandler
from coupon_management.models import Coupon
from coupon_management.forms import CouponForm
from django.http import JsonResponse
from django.db.models import OuterRef, Subquery
import json
import datetime
from django.utils import timezone
# Order management
from orders.models import Order, OrderProduct, Payment
from orders.forms import ChangeOrderStatusForm

# Create your views here.

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

    # print('=====================')
    # epoch_date = datetime.date(2023, 8, 1)
    # print(epoch_date.year)
    # print(epoch_date.strftime("%B"))
    # print(epoch_date.day)
    # current_date = datetime.date(2024, 8, 1)

    # months_list = [date.strftime("%b") for date in [epoch_date.replace(month=(epoch_date.month + i) % 12 + 1, year=epoch_date.year + (epoch_date.month + i - 1) // 12) for i in range((current_date.year - epoch_date.year) * 12 + current_date.month - epoch_date.month )]]

    # print(months_list)
    
    # print('=====================')


    orders = Order.objects.all()
    # cancelled_orders = orders.filter(order_status = 'Cancelled by User')
    # successfull_orders = orders.filter(order_status = 'Delivered')
    recent_orders = orders.filter()
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=15)
    start_date = timezone.make_aware(
        datetime.datetime.combine(start_date, datetime.time.min),
        timezone.get_current_timezone()
        )
    recent_orders = orders.filter(created_at__range=(start_date, today))
    categories = Category.objects.all()

    context = {
        'recent_orders': recent_orders,
        'categories': categories,
    }

    print("ADMIN-HOME")
    return render(request, 'admin_templates/admin_home.html', context)



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
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            is_active = form.cleaned_data['is_active']
            is_superadmin = form.cleaned_data['is_superadmin']
            is_staff = form.cleaned_data['is_staff']
            phone_number = '+91' + phone_number
            
            user = User.objects.create(
                first_name = first_name,
                last_name = last_name,
                email = email,
                phone_number = phone_number,
                password = password,
                is_active = is_active,
                is_superadmin = is_superadmin,
                is_staff = is_staff
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
            'form': form,
        }
    return render(request, 'admin_templates/create_user.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_signin(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin-home')
    
    if request.method == 'POST':
        raw_email = request.POST.get("email")
        password = request.POST.get("password")
        email = raw_email.lower().strip()

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
        phone_number = request.POST.get('phone_number')
        phone_number = '+91'+ phone_number
        user = User.objects.filter(phone_number = phone_number).first()
        if not user:
            # error messsage here
            messages.error(request, "Invalid phone number")
            return redirect('admin_otp_login')
        profile = UserProfile.objects.get(user = user)
        new_otp = random.randint(100000,999999)
        profile.otp = new_otp
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

            
    # products = Product.objects.all().annotate()
    products = Product.objects.annotate(
    image=Subquery(
        ProductVariant.objects.filter(product_id=OuterRef('pk')).values('thumbnail_image')[:1]
    )
    
)
    context = {'products': products,}
    return render(request, 'admin_templates/product_control/product_listing.html', context)


@check_isadmin
def product_control(request, prod_slug):
    product = Product.objects.get(prod_slug=prod_slug)
    product.is_available = not product.is_available
    product.save()
    return redirect('products')


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def add_product(request):
    product_form = ProductForm()
    variant_form = ProductVariantForm()
    variant_form.fields.pop('attributes', None)
    attributes = Attribute.objects.prefetch_related('attributevalue_set').filter(is_active=True)
    
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attributevalue_set.filter(is_active=True)
        attribute_dict[attribute.attribute_name] = attribute_values
    #to show how many atribute in frondend
    attribute_values_count = attributes.count()

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        variant_form = ProductVariantForm(request.POST, request.FILES)
        variant_form.fields.pop('attributes', None)
        attribute_ids=[]
        #getting all atributes
        for i in range(1,attribute_values_count+1):
            attribute_value_id = request.POST.get('attributes_'+str(i))
            if attribute_value_id != 'None':
                attribute_ids.append(int(attribute_value_id))
        
        if product_form.is_valid() and variant_form.is_valid():
            product = product_form.save()
            variant = variant_form.save(commit=False)
            variant.thumbnail_image = request.FILES.get('thumbnail_image')
            variant.product = product
            variant.save()
            variant.attributes.set(attribute_ids) # Save ManyToManyField relationships
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                ProductImage.objects.create(product_variant=variant, image=image)

            messages.success(request, 'Product added')
            return redirect('products')    
        
        else:
            print(product_form.errors)
            print("----------------------------------------------------")
            print(variant_form.errors)
            messages.error(request, variant_form.errors)
            
            context = {
                'product_form': product_form,
                'variant_form': variant_form,
                'attribute_dict': attribute_dict,
                }
            return render(request, 'admin_templates/product_control/product_add.html', context)
    else:
        context = {
            'product_form': product_form,
            'variant_form': variant_form,
            'attribute_dict': attribute_dict,
            }
    return render(request, 'admin_templates/product_control/product_add.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def product_update(request, prod_slug):

    product = Product.objects.get(prod_slug=prod_slug)
    product_variants = ProductVariant.objects.filter(product = product)
    form = ProductForm(instance = product)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated")
            return redirect('products')
            
        else:
            messages.error(request, form.errors)
            return redirect('product_update', prod_slug)
    
    context = {
        'form': form,
        'product_variants':product_variants, 
        'prod_slug': prod_slug,
        }
    return render(request, 'admin_templates/product_control/product_edit.html', context)
    
    
@check_isadmin
def add_product_variant(request, product_slug):
    try:
        product = Product.objects.get(prod_slug=product_slug) 
    except Product.DoesNotExist:
        return redirect('admin-all-product')
    except ValueError:
        return redirect('admin-all-product')
    
    product_variant_form = ProductVariantForm()
    product_variant_form.fields.pop('attributes', None)
    # attributes = Attribute.objects.all()
    attributes = Attribute.objects.prefetch_related('attributevalue_set')
    attribute_dict = {}
    for attribute in attributes:
        attribute_values = attribute.attributevalue_set.filter(is_active = True)
        attribute_dict[attribute.attribute_name] = attribute_values
    
    attribute_values_count = attributes.count()
    
    if request.method == 'POST':
        product_variant_form = ProductVariantForm(request.POST, request.FILES)
        print(product_variant_form.fields)
        product_variant_form.fields.pop('attributes', None)
        attribute_ids=[]
        #getting all attributes
        for i in range(1,attribute_values_count+1):
            attribute_value_id = request.POST.get('attributes_'+str(i))
            if attribute_value_id != 'None':
                attribute_ids.append(int(attribute_value_id))
        
        thumbnail_image = request.FILES.get('thumbnail_image')
        if product_variant_form.is_valid():
            variant = product_variant_form.save(commit=False)
            variant.product = product
            variant.thumbnail_image = thumbnail_image
            variant.save()
            variant.attributes.set(attribute_ids)    # Save ManyToManyField relationships
            variant.save()
            additional_images = request.FILES.getlist('additional_images')
            
            for image in additional_images:
                ProductImage.objects.create(product_variant=variant, image=image)
            messages.success(request, "Variant Created")
            
            return redirect('product_update',product_slug)
        else:
            print(product_variant_form.errors)
            messages.error(request, product_variant_form.errors)
            return redirect('product-variant-add', product_slug)
    
    context = {
        'product_variant_form': product_variant_form,
        'product_slug': product_slug,
        'product': product,
        'attribute_dict': attribute_dict,
        }
    return render(request, 'admin_templates/product_control/product_variant_create.html',context)


@check_isadmin
def product_variant_update(request, product_variant_slug):
    try:
        product_variant = ProductVariant.objects.get(product_variant_slug = product_variant_slug)
    except ProductVariant.DoesNotExist:
        return redirect('products')
    except ValueError:
        return redirect('products')
    
    product_variant_form = ProductVariantForm(instance = product_variant)
    current_additional_images = product_variant.product_images.all()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        image = request.FILES['file']
        image_id = request.POST['image_id']
        
        if image_id == 'thumbnail':
            image_id = None
            
        if image and image_id:
            try:
                additional_image = ProductImage.objects.get(id = image_id)
                additional_image.image = image
                additional_image.save()
                return JsonResponse({"status": "success",
                                     'new_image': additional_image.image.url,})
            except Exception as e :
                print(e)
    
        elif image and (not image_id):
            
            try:
                product_variant.thumbnail_image = image
                product_variant.save()
                
                return JsonResponse({
                    'status': 'success',
                    'new_image': product_variant.thumbnail_image.url,
                    })
            except Exception as e :
                print(e)
        else:
            return JsonResponse({"status": "error", "message": "image send error !"})
        
    
    if request.method == 'POST':
        product_variant_form = ProductVariantForm(request.POST,instance=product_variant)
        if product_variant_form.is_valid():
            variant = product_variant_form.save()
            
            messages.success(request, "Variant Updated")
            print("not working post")
            return redirect('product_update', product_variant.product.prod_slug)
        else:
            messages.error(request, product_variant_form.errors)
            context = {
                'product_variant_form': product_variant_form,
                'product_variant_slug':product_variant_slug,
                'product_variant': product_variant,
                'current_additional_images': current_additional_images,
            }
            
            return render(request, 'admin_templates/product_control/product_variant_edit.html', context)
        
    
    context = {
        'product_variant_form': product_variant_form,
        'product_variant_slug': product_variant_slug,
        'product_variant': product_variant,
        'current_additional_images': current_additional_images,
        }
    return render(request, 'admin_templates/product_control/product_variant_edit.html',context)
    


@check_isadmin
def delete_product_variant(request,product_variant_slug):
    
    try:
        product_variant = ProductVariant.objects.get(product_variant_slug=product_variant_slug)
    except ProductVariant.DoesNotExist:
        return redirect('products')
    except ValueError:
        return redirect('products')
    product_variant.delete()
    messages.error(request, "Variant Deleted ❌")
    return redirect('products')

    
    # <--------------------Brand management-------------------->
    
@check_isadmin
def all_brand(request):
    
    brands = Brand.objects.all()
    context = {
        'brands':brands
    }
    return render(request, 'admin_templates/product_control/all_brand.html',context)


@check_isadmin
def brand_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST' and is_ajax:
        data = json.load(request)
        brand_id = int(data['checkboxValue'])
        try:
            brand = Brand.objects.get(id =brand_id)
            brand.is_active = not brand.is_active
            brand.save()
            return JsonResponse({
                'status': 'success',
                'brand_status': brand.is_active,
                })
        except Exception as e :
            print(e)
            return JsonResponse({"status": "error", "message": e })
        



@check_isadmin
def create_brand(request):
    
    form = BrandForm()
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand created ")
            return redirect('admin_all_brand')
        else:
            messages.error(request, form.errors)
            context = {'form': form}
            return render(request, 'admin_templates/product_control/create_brand.html',context)
        
    context = {'form':form}
    return render(request, 'admin_templates/product_control/create_brand.html',context)


    
    
    # <--------------------Brand management end-------------------->
    
    
    # <--------------------Category management-------------------->
    
 

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
            'form': form,
        }
    return render(request, 'admin_templates/category-control/add_category.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@check_isadmin
def edit_category(request, cat_slug):
    
    category = Category.objects.get(cat_slug = cat_slug)
    form = CategoryForm(instance = category)
    
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
        'form': form
        }
    return render(request, 'admin_templates/category-control/edit_category.html', context)


@check_isadmin
def category_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':    
            data = json.load(request)
            cat_slug = data.get('checkboxValue')
            category = Category.objects.get(cat_slug = cat_slug)
            category.is_valid = not category.is_valid
            category.save()
            return JsonResponse({'context': 'ok'})
    else:
        return JsonResponse({'context': 'errror'})


@check_isadmin
def all_orders_admin(request):
    order_status = request.GET.get('status')
    
    if order_status:
        orders = Order.objects.filter(order_status__icontains=order_status).order_by('-created_at')
    else: 
        orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'admin_templates/order-control/all_orders.html',context)

@check_isadmin
def admin_order_history_detail(request,order_id):
    order = Order.objects.get(order_number = order_id)
    order_products = OrderProduct.objects.filter(order=order)
    total = 0
    for order_product in order_products:
        total += order_product.product_price * order_product.quantity
    
    try:
        payment = Payment.objects.filter(payment_id = order.payment)[0]
    except:
        payment = None
    form = ChangeOrderStatusForm(instance = order)
    context = {
        'order': order,
        'order_products': order_products,
        'total': total,
        'payment': payment,
        'form': form,
    }
    return render(request, 'admin_templates/order-control/order_details.html',context)

    
@check_isadmin
def change_order_status_admin(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST" and is_ajax:
        data = json.load(request)
        order_number = data.get('order_number')
        selected_option = data.get('selected_option')
        print("order number is  :",order_number)
        print("selected option is  :",selected_option)
        # Update the order status based on the order_number and selected_option
        try:
            order = Order.objects.get(order_number=order_number)
            order.order_status = selected_option
            if selected_option == 'Cancelled by Admin':
                try:
                    wallet = Wallet.objects.get(user = request.user,is_active=True)
                except Exception as e:
                    print(e)

                if order.payment.payment_method.method_name == 'COD':
                    wallet.balance += order.wallet_discount
                else:
                    wallet.balance += (order.order_total + order.wallet_discount)

                wallet.save()


            order.save()
            return JsonResponse({"status": "success", "selected_option": selected_option})
        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order Not Found"})
        # Return a JSON response indicating success or failure
        
    else:
        # Return a JSON response indicating an invalid request
        return JsonResponse({"status": "error", "message": "Invalid request"})
    
    
#Coupon management
    
@check_isadmin
def all_coupon(request):
    
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons,
        }
    return render(request, 'admin_templates/coupon_management/all_coupon.html', context)


@check_isadmin
def create_coupon(request):
    
    form = CouponForm()
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon created")
            return redirect('admin-all-coupon')
        else:
            context = {'form' : form}
            return render(request, 'admin_templates/coupon_management/coupon-create.html', context)
        
    context = {'form': form}
    return render(request, 'admin_templates/coupon_management/coupon-create.html', context)


@check_isadmin
def edit_coupon(request, id):
    
    try:
        coupon = Coupon.objects.get(id=id)
    except Coupon.DoesNotExist:
        return redirect('admin-all-coupon')
    except ValueError:
        return redirect('admin-all-coupon')

    form = CouponForm(instance=coupon)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated")
            return redirect('admin-all-coupon')
        else:
            messages.error(request, form.errors)
            return render(request, 'admin_templates/coupon_management/coupon-edit.html', {'form': form, 'id': id})
    context = {'form': form,'id': id}
    return render(request, 'admin_templates/coupon_management/coupon-edit.html', context)


#===========ATRIBUTE MANAGEMENT==================

def all_attributes(request):
    
    attributes = Attribute.objects.all()
    context = {
        'attributes': attributes,
    }
    return render(request, 'admin_templates/product_control/all_attributes.html',context)


def create_attribute(request):
    
    form = CreateAttributeForm()
    if request.method == 'POST':
        form = CreateAttributeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attibute Created ")
            return redirect('admin_all_attributes')
        else:
            context = {'form':form}
            return render(request, 'admin_templates/product_control/create_attribute.html',context)
        
    context = {'form':form}
    return render(request, 'admin_templates/product_control/create_attribute.html',context)


@check_isadmin
def attribute_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST' and is_ajax:
        data = json.load(request)
        attribute_id = int(data['checkboxValue'])
        try:
            attribute = Attribute.objects.get(id = attribute_id)
            attribute.is_active = not attribute.is_active
            attribute.save()
            return JsonResponse({
                'status': 'success',
                'attribute_status': attribute.is_active,
                })
        except Exception as e :
            print(e)
            return JsonResponse({"status": "error", "message": e })


#===========ATRIBUTE VALUE MANAGEMENT==================

def all_attribute_value(request):
    
    attribute_values = AttributeValue.objects.all()
    context = {
        'attribute_values': attribute_values,
    }
    return render(request, 'admin_templates/product_control/all_attribute_values.html',context)


def create_attribute_value(request):
    
    form = CreateAttributeValueForm()
    if request.method == 'POST':
        form = CreateAttributeValueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attribute Value Created ")
            return redirect('admin_all_attribute_value')
        else:
            context = {'form': form}
            return render(request, 'admin_templates/product_control/create_attribute_value.html',context)
        
    context = {'form':form}
    return render(request, 'admin_templates/product_control/create_attribute_value.html',context)
    
@check_isadmin
def attribute_value_control(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST' and is_ajax:
        data = json.load(request)
        attribute_value_id = int(data['checkboxValue'])
        try:
            attribute_value = AttributeValue.objects.get(id = attribute_value_id)
            attribute_value.is_active = not attribute_value.is_active
            attribute_value.save()
            return JsonResponse({
                'status': 'success',
                'attribute_status': attribute_value.is_active,
                })
        except Exception as e :
            print(e)
            return JsonResponse({"status": "error", "message": e })
        





        

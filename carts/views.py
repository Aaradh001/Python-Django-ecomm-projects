from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product,ProductVariant,Attribute,AttributeValue
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from accounts.forms import AddressBookForm
from accounts.models import AddressBook
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    try:
        product_variant = ProductVariant.objects.get(id = product_id)
    except Exception as e:
        print(e)
    
    if current_user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(product = product_variant, user = current_user)
            if cart_item.qty < cart_item.product.stock:
                cart_item.qty += 1
                cart_item.save()
            
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product_variant, qty=1, user=current_user)
            # cart_item.save()
        
        return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))   #getting the cart using the cart id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
        cart.save()

        try:
            cart_item = CartItem.objects.get(product = product_variant, cart = cart)
            cart_item.qty += 1
            cart_item.save()
            
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product_variant, qty=1, cart=cart)
        
        return redirect('cart')


def remove_cart(request, product_id):
    product_variant = get_object_or_404(ProductVariant, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product_variant, user = request.user)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product_variant, cart = cart)

        if cart_item.qty > 1:
            cart_item.qty -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart')


def del_cart_item(request, product_id):
    product_variant = get_object_or_404(ProductVariant, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product_variant)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product_variant, cart = cart)

    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, cart_items=None, quantity=0):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
        total_with_orginal_price = 0
        tax = 0
        grand_total = 0
        
        
        for cart_item in cart_items:
            total += cart_item.subtotal()
            total_with_orginal_price += ( cart_item.product.max_price * cart_item.qty)
            quantity += cart_item.qty

        discount = total_with_orginal_price - total
        tax = (5*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'max_total': total_with_orginal_price,
        'total': total,
        'discount': discount,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'total': total,
        'payable_amount': grand_total,
    }
        
    return render(request, 'store/cart.html', context)

@login_required(login_url = 'signin')
def checkout(request, total=0, cart_items=None, quantity=0):
    try:
        total_with_orginal_price = 0
        tax = 0
        cart_items = CartItem.objects.filter(user = request.user, is_active =True)
        
        for cart_item  in cart_items:
            total += cart_item.subtotal()
            quantity += cart_item.qty
            total_with_orginal_price += cart_item.product.max_price * cart_item.qty
        tax = (5*total)/100
        discount = total_with_orginal_price - total
    except ObjectDoesNotExist:
        pass
    
    address_form = AddressBookForm()
    addresses = AddressBook.objects.filter(user=request.user,is_active=True).order_by('-is_default')
    context = {
        'max_total': total_with_orginal_price,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': total,
        'addresses': addresses,
        'address_form': address_form,
        'discount': discount,
        }
    return render(request, 'store/checkout.html', context)


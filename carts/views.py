from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
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
    product = Product.objects.get(id = product_id)
    
    if current_user.is_authenticated:
                
        try:
            cart_item = CartItem.objects.get(product = product, user = current_user)
            cart_item.qty += 1
            cart_item.save()
            
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, qty=1, user=current_user)
            cart_item.save()
        
        return redirect('cart')
    
    else:

        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))   #getting the cart using the cart id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id= _cart_id(request))

        cart.save()
        
        try:
            cart_item = CartItem.objects.get(product = product, cart = cart)
            cart_item.qty += 1
            cart_item.save()
            
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, qty=1, cart=cart)
            cart_item.save()
        
        return redirect('cart')

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user = request.user)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart = cart)

        if cart_item.qty > 1:
            cart_item.qty -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart')




def del_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user = request.user, product=product)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart = cart)

    cart_item.delete()
    return redirect('cart')


def cart(request, total = 0, cart_items = None, quantity = 0):
    try:
        tax = 0
        grand_total = 0
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active =True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active =True)
            
        for cart_item  in cart_items:
            total += cart_item.product.price * cart_item.qty
            quantity += cart_item.qty

        tax         = (5*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    address_form = AddressBookForm()
    
    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   : grand_total,
    }
        
    return render(request, 'store/cart.html', context)

@login_required(login_url='signin')
def checkout(request, total = 0, cart_items = None, quantity = 0):
    try:
        tax = 0
        grand_total = 0
        cart_items = CartItem.objects.filter(user = request.user, is_active =True)
        
        for cart_item  in cart_items:
            total += cart_item.product.price * cart_item.qty
            quantity += cart_item.qty

        tax         = (5*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    address_form = AddressBookForm()
    addresses = AddressBook.objects.filter(user=request.user,is_active=True).order_by('-is_default')
    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   : grand_total,
        'addresses'      : addresses,
        'address_form'  : address_form,
    }
        
    return render(request, 'store/checkout.html', context)
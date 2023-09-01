from django.shortcuts import render
from category_management.models import Category
from carts.models import CartItem
from carts.views import _cart_id 
from store.models import Product, ProductImage
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_control
# Create your views here.


def product_store(request, cat_slug = None):
    if cat_slug:
        category = Category.objects.get(cat_slug = cat_slug)
        if not category.parent:
            categories = Category.objects.filter(parent = category)
            q1 = Q(category__in = categories)
            q2 = Q(is_available = True)
            
            combined_q = q1 & q2
            
            products =  Product.objects.filter(combined_q).order_by('id')
            paginator = Paginator(products, 2)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
        else:
            q1 = Q(category = category)
            q2 = Q(is_available = True)
            combined_q = q1 & q2
            products = Product.objects.filter(combined_q).order_by('id')
            paginator = Paginator(products, 2)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
    
    else:
        products = Product.objects.filter(is_available = True).order_by('id')
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    
    context = {
        'products'      : paged_products,
        }
    
    return render(request, 'all_product_display.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_detail(request, cat_slug, prod_slug):
    
    try:
        single_product = Product.objects.get(category__cat_slug = cat_slug, prod_slug = prod_slug)
        if request.user.is_authenticated:
            in_cart = CartItem.objects.filter(user = request.user, product = single_product).exists()
        else:
            in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
            
        add_images = ProductImage.objects.filter(product = single_product)
        
    except Exception as e:
        raise e
        
    context = {
        'single_product'    : single_product,
        'in_cart'           : in_cart,
        'add_images'        : add_images,
    }

    return render(request, 'product_detail.html',context)
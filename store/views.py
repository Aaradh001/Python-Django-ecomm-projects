from django.shortcuts import render,get_object_or_404, redirect
from category_management.models import Category
from carts.models import CartItem
from carts.views import _cart_id 
from store.models import Product, ProductImage, ProductVariant, Brand, Attribute, AttributeValue
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_control
from django.contrib.auth import get_user_model
from django.http import HttpResponse
# Create your views here.
              
User = get_user_model()
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    products = Product.objects.filter(is_available = True)
    product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(is_active=True).order_by('stock')
    print("The product variants are :")
    print(product_variants)
    print("Exit")
    context = {
        'products': products,
        'product_variants': product_variants,
    }
    
    return render(request, 'index.html', context)





def product_store(request, cat_slug=None, offer_slug=None):

    price_min = request.GET.get('price-min')
    price_max = request.GET.get('price-max')
    if cat_slug:
        try:
            category = get_object_or_404(Category, cat_slug = cat_slug)
        except Exception as e:
            print(e)
            return redirect('product_store')

            
        if not category.parent:
            categories = Category.objects.filter(parent = category)
            q1 = Q(product__category__in = categories)
            q2 = Q(is_active = True)
            
            combined_q = q1 & q2
            
            product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(combined_q).order_by('stock')
            # product_variants_count = product_variants.count()

        else:
            q1 = Q(product__category = category)
            q2 = Q(is_active = True)
            combined_q = q1 & q2
            product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(combined_q).order_by('stock')
            # product_variants_count = product_variants.count()
    else:
        product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(is_active=True).order_by('stock')

    

    
    #price filter
    if price_min:
        product_variants = product_variants.filter(sale_price__gte=price_min)
    if price_max:
        product_variants = product_variants.filter(sale_price__lte=price_max)

    # Get all attribute names from the request and avoid certain parameters
    attribute_names = [key for key in request.GET.keys() if key not in ['keyword','page','price-min','price-max','RATING']]
    print(request.GET.keys())
    #other filter
    for attribute_name in attribute_names:
        attribute_values = request.GET.getlist(attribute_name)
        if attribute_values:
            product_variants=product_variants.filter(atributes__atribute_value__in=attribute_values)



    

    paginator = Paginator(product_variants, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)




    context = {
        'product_variants'       : paged_products,
        'product_variants_count' : len(product_variants),
        }
    
    return render(request, 'all_product_display.html', context)

def product_variant_detail(request, cat_slug, variant_slug):
    try:
        single_product = ProductVariant.objects.select_related('product').prefetch_related('attributes','product_images').get(
                    product__category__cat_slug=cat_slug,
                    product_variant_slug=variant_slug,
                    is_active=True)
        if request.user.is_authenticated:
            in_cart = CartItem.objects.filter(user = request.user, product = single_product).exists()
            print(in_cart)
        else:
            in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
            
        add_images = ProductImage.objects.filter(product_variant = single_product)
        product_variants = ProductVariant.objects.filter(product=single_product.product,is_active=True)
        product_variants_count=product_variants.count()
        
    except Exception as e:
        raise e
        
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'add_images': add_images,
        'product_variants': product_variants,
        'product_variants_count': product_variants_count,
    }

    return render(request, 'product_detail.html',context)


def search(request):
    print("hi im aaradh ")
    other_keys = set(request.GET.keys())-{'keyword'}
    if other_keys:
        return redirect('product_store')

    if 'keyword' in  request.GET:
        keyword = request.GET['keyword']
        
        if keyword:
            keywords = keyword.split(" ")
            products=[]
            all_products=ProductVariant.objects.all()
            searchresult=[]
            # while i<len(keywords):
            for keyword in keywords:
                products = all_products.filter(Q(product__description__icontains = keyword) | Q(product__product_name__icontains = keyword) | Q(product__brand__brand_name__icontains = keyword)| Q(product__category__category_name__icontains = keyword)| Q(attributes__attribute_value__icontains = keyword))
                if not products:
                    searchresult.append("noword")
                    continue
                else:
                    searchresult.append(keyword)
                    all_products=products
            products = set(all_products)
            context = {
                'product_variants'      : products,
                'product_variants_count' : len(products),
            }
    return render(request, 'all_product_display.html', context)
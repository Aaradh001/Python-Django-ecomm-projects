from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic import View
from .models import CategoryOffer, ProductOffer
from store.models import ProductVariant
from django.shortcuts import get_object_or_404
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator 
from datetime import datetime

# Create your views here.
class all_offers_store(ListView):  
    # model = CategoryOffer  
    template_name = 'offers/all_offers.html'
    # context_object_name = 'categoryOffers'
    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer = CategoryOffer.objects.filter(is_active=True, expire_date__gte=datetime.now())
        
        context['category_offers'] = CategoryOffer.objects.filter(is_active=True, expire_date__gte=datetime.now()) 
        context['product_offers'] = ProductOffer.objects.filter(is_active=True, expire_date__gte=datetime.now()) 
       
        return context


class category_offer_product(View):
    def get(self, request, offer_slug, category_slug=None):

        price_min = request.GET.get('price-min')
        price_max = request.GET.get('price-max')
        
        # #wishlist
        # if request.user.is_authenticated:  
        #     wishlist,created= Wishlist.objects.get_or_create(user=request.user)
        #     wishlist_items = WishlistItem.objects.filter(wishlist=wishlist, is_active=True).values_list('product_id', flat=True)
        # else:
        #     wishlist_items =[]
    
        try:
            category_offer = get_object_or_404(CategoryOffer, category_offer_slug=offer_slug)
        except:
            return redirect('store')
    
        categories = category_offer.category.filter(is_valid=True)
        
        if category_slug:
            category = category_offer.category.filter(is_valid=True, cat_slug=category_slug)
            product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(product__category__in=category,is_active=True)
            product_variants_count = product_variants.count()
        else:
            product_variants = ProductVariant.objects.select_related('product').prefetch_related('attributes').filter(product__category__in=categories,is_active=True)
            product_variants_count = product_variants.count()
        
        #price filter 
        if price_min:
            product_variants = product_variants.filter(sale_price__gte=price_min)
        if price_max:
            product_variants = product_variants.filter(sale_price__lte=price_max)
            
            
        # Get all attribute names from the request avoid certain parameters
        attribute_names = [key for key in request.GET.keys() if key not in ['query','page','price-min','price-max']]
        
            #other filter
        for attribute_name in attribute_names:
            attribute_values = request.GET.getlist(attribute_name)
            if attribute_values:
                product_variants=product_variants.filter(attributes__attribute_value__in=attribute_values)
        
        product_variants_count = product_variants.count()
        
    
        # paginator start
        paginator = Paginator(product_variants,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
            
        context = {
            'category_offer': category_offer,
            'product_variants': paged_products,
            'product_variants_count': product_variants_count,
            'all_category_list': categories,
            'price_min': price_min,
            'price_max': price_max,
            # 'wishlist_items': wishlist_items
            }
        return render(request, 'offers/category_offer_items.html.html', context)



class product_offer_product(View):
    def get(self, request, offer_slug):

        price_min = request.GET.get('price-min')
        price_max = request.GET.get('price-max')
        
        # #wishlist
        # if request.user.is_authenticated:  
        #     wishlist,created= Wishlist.objects.get_or_create(user=request.user)
        #     wishlist_items = WishlistItem.objects.filter(wishlist=wishlist, is_active=True).values_list('product_id', flat=True)
        # else:
        #     wishlist_items =[]
            
    
        try:
            product_offer = get_object_or_404(ProductOffer, product_offer_slug=offer_slug)
        except:
            return redirect('store')
    
        products = product_offer.product.filter(is_active=True).values_list('sku_id')
       
       
        product_variants = ProductVariant.objects.select_related('product').prefetch_related('atributes').filter(sku_id__in=products,is_active=True)
        product_variants_count = product_variants.count()
        
        #price filter 
        if price_min:
            product_variants = product_variants.filter(sale_price__gte=price_min)
        if price_max:
            product_variants = product_variants.filter(sale_price__lte=price_max)
            
            
        # Get all attribute names from the request avoid certain parameters
        attribute_names = [key for key in request.GET.keys() if key not in ['query','page','price-min','price-max']]
        
            #other filter
        for attribute_name in attribute_names:
            attribute_values = request.GET.getlist(attribute_name)
            if attribute_values:
                product_variants=product_variants.filter(atributes__atribute_value__in=attribute_values)
        
        product_variants_count = product_variants.count()
        
    
        # paginator start
        paginator = Paginator(product_variants,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
            
        context = {
            'product_offer': product_offer,
            'product_variants': paged_products,
            'product_variants_count': product_variants_count,
            'price_min': price_min,
            'price_max': price_max,
            # 'wishlist_items':wishlist_items
                
            }
        return render(request,'store/offer_items_product.html',context)
    
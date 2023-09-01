from django.shortcuts import render
from category_management.models import Category

# Create your views here.
def category_listing(request,):
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
        }
    
    return render(request, 'all_product_display.html',context)
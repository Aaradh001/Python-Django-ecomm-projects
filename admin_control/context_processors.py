from category_management.models import Category

def admin_categories(request):
    categories = Category.objects.all()
    return dict(categories = categories)

from category_management.models import Category

def admin_categories(request):
    categories = Category.objects.al()
    return dict(categories = categories)

from category_management.models import Category

def menu_links(request):
    all_categories_list = Category.objects.filter(is_valid =True)
    return dict(all_categories_list = all_categories_list)
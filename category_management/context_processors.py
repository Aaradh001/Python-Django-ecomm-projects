from category_management.models import Category

def menu_links(request):
    links = Category.objects.filter(is_valid =True)
    return dict(links = links)
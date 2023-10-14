from category_management.models import Category
from store.models import Attribute

def menu_links(request):
    all_categories_list = Category.objects.filter(is_valid =True)
    return dict(all_categories_list = all_categories_list)


def all_attribute(request):
     all_attribute_list = Attribute.objects.filter(is_active=True)
     return dict(all_attribute_list=all_attribute_list)

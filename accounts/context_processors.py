from django.contrib.auth import get_user_model





User = get_user_model()
def menu_links(request):
    username = request.user.first_name if request.user.is_authenticated else None
    return dict(username = username )
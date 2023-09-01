from django.urls import path
from carts import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove-cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('delete-cart-item/<int:product_id>/', views.del_cart_item, name='del_cart_item'),
 
    path('checkout/', views.checkout, name='checkout'),
]
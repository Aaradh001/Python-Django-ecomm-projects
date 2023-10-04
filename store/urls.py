from django.urls import path
from store import views


urlpatterns = [
    path('', views.home, name='user_home'),
    path('store/',views.product_store, name='product_store'),
    path('store/category/<slug:cat_slug>/',views.product_store, name='product_by_category'),
    path('store/category/<slug:cat_slug>/<slug:variant_slug>',views.product_variant_detail, name='product_variant_detail'),
    path('store/search/',views.search, name='search'),
]
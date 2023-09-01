from django.urls import path
from store import views

urlpatterns = [
    path('',views.product_store, name='product_store'),
    path('<slug:cat_slug>/',views.product_store, name='product_by_category'),
    path('<slug:cat_slug>/<slug:prod_slug>',views.product_detail, name='product_detail'),
]
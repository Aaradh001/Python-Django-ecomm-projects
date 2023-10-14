from django.urls import path
from . import views


urlpatterns = [
    path("store/offers", views.all_offers_store.as_view(), name="store-all-offers"),
    path("store/offers/category/<str:offer_slug>", views.category_offer_product.as_view(), name="store-category-offers"),
    path("store/offers/category/<str:offer_slug>/<str:category_slug>", views.category_offer_product.as_view(), name="store-category-offers-each"),
    ]



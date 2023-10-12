from django.urls import path
from . import views


urlpatterns = [
    path("store/offers", views.all_offers_store.as_view(), name="store-all-offers"),
    ]



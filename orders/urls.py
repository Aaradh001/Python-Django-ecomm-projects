from django.urls import path
from orders import views


urlpatterns = [
    path('', views.order_summary, name='order_summary'),
    path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
]
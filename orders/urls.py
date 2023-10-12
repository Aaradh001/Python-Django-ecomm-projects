from django.urls import path
from orders import views
from coupon_management.views import coupon_verify


urlpatterns = [
    path('order-summary/', views.order_summary, name='order_summary'),
    path('place-order/', views.place_order, name='place_order'),
    
    path("payment/success/", views.payment_success, name="payment-success"),
    path("payment/failed/", views.payment_failed, name="payment-failed"),
    
    path("order_complete", views.order_complete, name="order_complete"),
    path("order-success/download-invoice/<str:invoice_number>", views.generate_invoice, name="generate_invoice"),
    
    path("order-summary/coupon/verify/", coupon_verify, name="coupon_verify"),
]
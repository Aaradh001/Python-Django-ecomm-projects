from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.home, name='user_home'),
    path('signin/',views.user_signin, name='signin'),
    path('signup/',views.user_signup, name='user_signup'),
    path('signout',views.signout, name='signout'),
    path('otp-login-user/', views.otp_generation, name='user_otp_login'),
    path('enter-otp-user/<str:uid>/', views.enter_otp, name='user_enter_otp'),
    path('user/dashboard/', views.dashboard, name='dashboard'),
    path('user/myaddress/', views.my_address, name='my_address'),
    path('user/add-address/<str:source>', views.add_address, name='add_address'),
    path('user/default-address/<int:id>', views.default_address, name='default_address'),
    path('user/delete-address/<int:id>', views.address_delete, name='address_delete'),
]
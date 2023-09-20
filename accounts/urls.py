from django.urls import path
from accounts import views

urlpatterns = [
    
    path('signin/',views.user_signin, name='signin'),
    path('signup/',views.user_signup, name='user_signup'),
    path('signout/',views.signout, name='signout'),
    path('otp-login-user/', views.otp_generation, name='user_otp_login'),
    path('enter-otp-user/<str:uid>/', views.enter_otp, name='user_enter_otp'),
   
#    Address management
    path('user/myaddress/', views.my_address, name='my_address'),
    path('user/add-address/<str:source>', views.add_address, name='add_address'),
    path('user/default-address/<int:id>', views.default_address, name='default_address'),
    path('user/delete-address/<int:id>', views.address_delete, name='address_delete'),
    
    # Profile and order handling
    
    path('user/myaccount/', views.user_account, name='user_account'),
    path('user/order-history/', views.order_history, name='order_history'),
    path('user/order-history/<str:order_id>', views.order_history_detail, name='order-history-detail'),
    
    # Order cancelling & return
    path("cancel/<str:order_id>/", views.order_cancel_user, name="order_cancel_user"),
    path("return/<str:order_id>/", views.order_return_user, name="order_return_user"),
    
    # profile pic update 
    
    path("users/update/profilepic", views.update_profile_picture, name="update_profile_picture"),

    
    
    # user field update ajax
    path("users/basic/update", views.update_fields_user, name="update_fields_user"),
    
    # Mobile number update ajax
    path("users/update/mobile", views.change_mobile_with_otp, name="change_mobile_with_otp"),
    path("users/update/mobile/verify", views.change_mobile_with_otp_verify, name="change_mobile_with_otp_verify"),
    
    
    # Email id update ajax
    path("users/update/email", views.change_email_with_email, name="change_email_with_email"),
    path("users/update/email/verify", views.change_email_with_email_verify, name="change_email_with_email_verify"),
    
    
    # Password update with old password ajax
    path("users/basic/changepassword", views.change_user_password_with_oldpass, name="change_user_password_with_oldpass"),
    
    
    # ===========forgot password============
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('resetpassword_validate/<slug:uid>/<token>/ ', views.resetpassword_validate, name='resetpassword_validate'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    
    
    # path('my-orders/', views.my_orders, name='my_orders'),





]
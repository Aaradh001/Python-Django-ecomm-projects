from django.urls import path
from admin_control import views

urlpatterns = [

# <-----------------------Admin-authentication---------------------->
    
    path('admin-signin/', views.admin_signin, name='admin_signin'),
    path('admin-signout/', views.admin_signout, name='admin_signout'),
    path('loginwithotp/', views.admin_otp_generation, name='admin_otp_login'),
    path('enter-otp/<str:uid>/', views.enter_otp, name='enter_otp'),
    path('',views.admin_home, name='admin-home'),
   
# <--------------------------User-management------------------------->

    path('user-management/',views.user_management, name='user_management'),
    path('usermanagement/b2u/<int:id>',views.block_or_unblock, name='block_unblock'),
    path('usermanagement/edit-user/<int:id>',views.user_edit, name='user_edit'),
    path('admin-add-user', views.user_create, name='create_user'),
   
# <--------------------------product-control-------------------------->

    path('products/', views.product_listing, name='products'),
    path('product-management/e2d/<int:id>/',views.product_control, name='product_control'),
    path('product-management/update-product/<int:id>/',views.product_update, name='product_update'),
    path('add-product/', views.add_product, name='add_product'),
    
    
# <--------------------------Category management-------------------------->
    path('add-category/', views.add_category, name='add_category'),
    path('update-category/<str:cat_slug>', views.edit_category, name='edit_category'),
    path('category-management/a2d/<str:cat_slug>/', views.category_control, name='category_control'),
    path('category-control/', views.category_control, name='category_control'),

# <--------------------------Order management URLS--------------------------->
    path('all-orders/', views.all_orders_admin, name='all_orders_admin'),
    path("orders/detail/<str:order_id>", views.admin_order_history_detail, name="admin-order-history-detail"),
    path("orders/detail/change/status", views.change_order_status_admin, name="change_order_status_admin"),


# <--------------------------Coupon management URLS--------------------------->
    path("coupon", views.all_coupon, name="admin-all-coupon"),
    path("coupon/create", views.create_coupon, name="admin-coupon-create"),
    path("coupon/edit/<int:id>", views.edit_coupon, name="admin-coupon-edit"),

]

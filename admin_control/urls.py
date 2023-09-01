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

# <--------------------------Practice URLS-------------------------->


    
    
#     path('', views.admin_dashboard, name='admin_dashboard'),
#     # path('signin/',views.user_signin, name='signin'),
#     # path('desthome/',views.user_desthome, name='desthome'),
#     # path('admindesthome/',views.admin_desthome, name='admindesthome'),
#     # path('signout',views.signout, name='signout'),
#     # path('register/',views.user_register, name='user_register'),
#     # path('adminregister/', views.admin_register, name='admin_register'),
#     # path('user-home/',views.user_home, name='user_home'),
#     # path('admin-home/',views.admin_home, name='admin_home'),
#     # path('logout/',views.logoutpage, name='logout'),
#     # path('admin-home/user/update/<int:id>',views.useredit, name='useredit'),
#     # path('admin-home/user/delete/<int:id>',views.user_delete, name='user_delete'),
#     # path('admin-home/create-user',views.userCreate, name='user_create'),
]
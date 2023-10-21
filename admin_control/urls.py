from django.urls import path
from admin_control import views

urlpatterns = [

# <-----------------------Admin-authentication---------------------->
    
    path('admin-signin/', views.admin_signin, name='admin_signin'),
    path('admin-signout/', views.admin_signout, name='admin_signout'),
    path('loginwithotp/', views.admin_otp_generation, name='admin_otp_login'),
    path('enter-otp/<str:uid>/', views.enter_otp, name='enter_otp'),
    path('',views.admin_home, name='admin-home'),
   
# <-------------------------- Admin-dashboard------------------------->
    path('sales-data/year/',views.admin_home, name='yearly_sales_data'),

# <--------------------------User-management------------------------->

    path('user-management/',views.user_management, name='user_management'),
    path('usermanagement/b2u/<int:id>',views.block_or_unblock, name='block_unblock'),
    path('usermanagement/edit-user/<int:id>',views.user_edit, name='user_edit'),
    path('admin-add-user', views.user_create, name='create_user'),
   
# <--------------------------product-control-------------------------->

    path('products/', views.product_listing, name='products'),
    path('product-management/e2d/<str:prod_slug>/',views.product_control, name='product_control'),
    path('product-management/update-product/<str:prod_slug>/',views.product_update, name='product_update'),
    path('add-product/', views.add_product, name='add_product'),
    
    path("product/edit/variant/addnew/<slug:product_slug>/", views.add_product_variant, name="product-variant-add"),
    path("product/edit/variant/<slug:product_variant_slug>/", views.product_variant_update, name="admin-product-variant-update"),
    path("product/delete/variant/<slug:product_variant_slug>/", views.delete_product_variant, name="admin-product-variant-delete"),
    path("product/delete/variant/<slug:product_variant_slug>/", views.delete_product_variant, name="admin-product-variant-delete"),
    
    # AJAX requests image updation
    path("product/variant/update/additional-images/<slug:product_variant_slug>/", views.product_variant_update, name="admin_product_variant_update_ajax"),
    
    # Brand management
    path("brand", views.all_brand, name="admin_all_brand"),
    path("brand/create", views.create_brand, name="admin_brand_create"),
    
    # Attribute management
    path("variant-attribute/", views.all_attributes, name="admin_all_attributes"),
    path("variant-attribute/create", views.create_attribute, name="admin_create_attribute"),

    #atribute value management
    path("variant-atribute_value", views.all_attribute_value, name="admin_all_attribute_value"),
    path("variant-attribute_value/create", views.create_attribute_value, name="admin_attribute_value_create"),


    # Ajax brand control
    path("brand/brandcontrol/", views.brand_control, name="admin-brand-control"),

    # Ajax attribute control
    path("attribute/attributecontrol/", views.attribute_control, name="admin-attribute-control"),
    
    # Ajax attribute-value control
    path("attribute-value/attribute-value-control/", views.attribute_value_control, name="admin-attribute-value-control"),
    
    
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

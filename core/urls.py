from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_phone, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('user/profile/', views.user_profile, name='user_profile'),

    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('toggle-wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.track_orders, name='track_orders'),

    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    path('upi-payment/', views.upi_payment_page, name='upi_payment'),

    path('delivery/login/', views.delivery_login, name='delivery_login'),
    path('delivery/register/', views.delivery_register, name='delivery_register'),
    path('delivery/logout/', views.delivery_logout, name='delivery_logout'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/order/<int:order_id>/update/', views.update_order_status, name='update_order_status'),

]

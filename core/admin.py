from django.contrib import admin
from .models import Category, Product, Review, Order, DeliveryPartner
from django.contrib.auth import get_user_model

User = get_user_model()


admin.site.register(Category)
admin.site.register(Product)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'name', 'email', 'last_login', 'is_active')
    search_fields = ('phone', 'name', 'email')
    list_filter = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'created_at')
    search_fields = ('user__phone', 'product__title')
    list_filter = ('rating', 'created_at')


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'joined_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_method', 'order_date', 'delivery_partner']
    list_editable = ['delivery_partner']
    search_fields = ['user__phone', 'delivery_partner__name']
    list_filter = ['status', 'payment_method']

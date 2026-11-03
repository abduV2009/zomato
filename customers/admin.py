from django.contrib import admin
from .models import Customer, DeliveryAddress, RestaurantInquiry, PartnerApplication


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id","user","phone")


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ("label", "customer", "city", "is_default")
    list_filter = ("is_default", "city")


@admin.register(RestaurantInquiry)
class RestaurantInquiryAdmin(admin.ModelAdmin):
    list_display = ("restaurant_name", "inquiry_type", "name", "email", "created_at")
    list_filter = ("inquiry_type",)


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = ("place_name", "place_type", "owner_name", "email", "city", "created_at")
    list_filter = ("place_type", "city")

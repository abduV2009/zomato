from django.urls import path
from . import views


urlpatterns = [

    path("profile/", views.profile, name="profile"),
    path("addresses/add/", views.address_create, name="address_create"),
    path("addresses/<int:id>/edit/", views.address_update, name="address_update"),
    path("addresses/<int:id>/delete/", views.address_delete, name="address_delete"),
    path("suggest-restaurant/", views.restaurant_inquiry, name="restaurant_inquiry"),
    path("partner-apply/", views.partner_application, name="partner_application"),

    path("", views.customer_list, name="customer_list"),

    path(
        "create/",
        views.customer_create,
        name="customer_create"
    ),

    path(
        "update/<int:id>/",
        views.customer_update,
        name="customer_update"
    ),

    path(
        "delete/<int:id>/",
        views.customer_delete,
        name="customer_delete"
    ),
]


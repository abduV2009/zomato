# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class DeliveryAddress(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="delivery_addresses",
    )
    label = models.CharField(max_length=50, default="Home")
    recipient_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.label} - {self.customer.user.username}"


class RestaurantInquiry(models.Model):
    INQUIRY_TYPES = [
        ("missing", "Missing restaurant"),
        ("unlisted", "Unlisted restaurant"),
        ("new", "New restaurant"),
    ]
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    restaurant_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.restaurant_name} ({self.get_inquiry_type_display()})"


class PartnerApplication(models.Model):
    PLACE_TYPES = [
        ("restaurant", "Restaurant"),
        ("kitchen", "Cloud kitchen"),
    ]
    owner_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    place_type = models.CharField(max_length=20, choices=PLACE_TYPES)
    place_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.place_name} ({self.get_place_type_display()})"

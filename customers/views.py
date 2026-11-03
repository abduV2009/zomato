
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, DeliveryAddress, RestaurantInquiry, PartnerApplication
from food_delivery.decorator import superuser_required

# CREATE
def customer_create(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )

        Customer.objects.create(
            user=user,
            phone=phone,
            address=address
        )

        return redirect("login")

    return render(request, "customers/customer_form.html")


@login_required
def profile(request):
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"phone": "", "address": ""},
    )

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.save()
        customer.phone = request.POST.get("phone", "").strip()
        customer.save()
        return redirect("profile")

    return render(request, "customers/profile.html", {
        "customer": customer,
        "addresses": customer.delivery_addresses.all(),
    })


def _address_values(request):
    return {
        "label": request.POST.get("label", "Home").strip() or "Home",
        "recipient_name": request.POST.get("recipient_name", "").strip(),
        "phone": request.POST.get("phone", "").strip(),
        "address_line": request.POST.get("address_line", "").strip(),
        "city": request.POST.get("city", "").strip(),
        "state": request.POST.get("state", "").strip(),
        "postal_code": request.POST.get("postal_code", "").strip(),
        "is_default": request.POST.get("is_default") == "on",
    }


def _set_default_address(customer, address):
    if address.is_default:
        customer.delivery_addresses.exclude(id=address.id).update(is_default=False)


@login_required
def address_create(request):
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"phone": "", "address": ""},
    )
    if request.method == "POST":
        address = DeliveryAddress.objects.create(
            customer=customer,
            **_address_values(request),
        )
        _set_default_address(customer, address)
        if request.POST.get("next") == "cart":
            return redirect("cart_detail")
        return redirect("profile")
    return render(request, "customers/address_form.html", {
        "customer": customer,
        "next": request.GET.get("next"),
    })


@login_required
def address_update(request, id):
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"phone": "", "address": ""},
    )
    address = get_object_or_404(DeliveryAddress, id=id, customer=customer)
    if request.method == "POST":
        for field, value in _address_values(request).items():
            setattr(address, field, value)
        address.save()
        _set_default_address(customer, address)
        return redirect("profile")
    return render(request, "customers/address_form.html", {
        "address": address,
        "customer": customer,
    })


@login_required
def address_delete(request, id):
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"phone": "", "address": ""},
    )
    address = get_object_or_404(DeliveryAddress, id=id, customer=customer)
    if request.method == "POST":
        address.delete()
    return redirect("profile")


# READ
@superuser_required
def customer_list(request):

    customers = Customer.objects.all()

    return render(
        request,
        "customers/customer_list.html",
        {"customers": customers}
    )


# UPDATE (admin customer management)
@superuser_required
def customer_update(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":

        customer.user.username = request.POST.get("username")
        customer.user.save()

        customer.phone = request.POST.get("phone")
        customer.address = request.POST.get("address")

        customer.save()

        return redirect("customer_list")

    return render(
        request,
        "customers/customer_form.html",
        {"customer": customer}
    )


# DELETE (admin customer management)
@superuser_required
def customer_delete(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == "POST":
        customer.user.delete()

        return redirect("customer_list")

    return render(
        request,
        "customers/customer_confirm_delete.html",
        {"customer": customer}
    )


def restaurant_inquiry(request):
    if request.method == "POST":
        RestaurantInquiry.objects.create(
            name=request.POST.get("name", "").strip(),
            email=request.POST.get("email", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            inquiry_type=request.POST.get("inquiry_type", "missing"),
            restaurant_name=request.POST.get("restaurant_name", "").strip(),
            city=request.POST.get("city", "").strip(),
            details=request.POST.get("details", "").strip(),
        )
        messages.success(request, "Thanks. We received your restaurant inquiry.")
        return redirect("restaurant_inquiry")
    return render(request, "customers/restaurant_inquiry.html")


def partner_application(request):
    if request.method == "POST":
        PartnerApplication.objects.create(
            owner_name=request.POST.get("owner_name", "").strip(),
            email=request.POST.get("email", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            place_type=request.POST.get("place_type", "restaurant"),
            place_name=request.POST.get("place_name", "").strip(),
            city=request.POST.get("city", "").strip(),
            address=request.POST.get("address", "").strip(),
            description=request.POST.get("description", "").strip(),
        )
        messages.success(request, "Thanks. We received your application.")
        return redirect("partner_application")
    return render(request, "customers/partner_application.html")

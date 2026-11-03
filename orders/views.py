from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from food_delivery.decorator import *
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
from customers.models import Customer, DeliveryAddress


DELIVERY_FEE = Decimal("40.00")
FREE_DELIVERY_THRESHOLD = Decimal("499.00")


def _cart(request):
    """Return the visitor's cart, stored in their session."""
    return request.session.get("cart", {})


def _source_key(product):
    if product.restaurant_ref_id:
        return f"place:{product.restaurant_ref_id}"
    name = (product.restaurant or "").strip().lower()
    return f"name:{name}" if name else f"item:{product.id}"


def _source_label(product):
    kitchen = product.restaurant_ref
    if kitchen:
        return kitchen.name
    return product.restaurant or product.name


def _cart_source_conflict(cart, product):
    if not cart:
        return None
    existing = (
        Product.objects.filter(id__in=cart.keys())
        .select_related("restaurant_ref")
        .first()
    )
    if existing and _source_key(existing) != _source_key(product):
        return existing
    return None


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session["cart_count"] = sum(cart.values())
    request.session.modified = True


def cart_detail(request):
    cart = _cart(request)
    products = Product.objects.filter(id__in=cart.keys(), is_available=True).select_related(
        "restaurant_ref"
    )
    items = []
    total = Decimal("0.00")
    cart_source = ""
    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
        if not cart_source:
            cart_source = _source_label(product)

    delivery_fee = 0 if total >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    addresses = []
    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={"phone": "", "address": ""},
        )
        addresses = customer.delivery_addresses.all()

    return render(request, "orders/cart.html", {
        "items": items,
        "subtotal": total,
        "delivery_fee": delivery_fee,
        "grand_total": total + delivery_fee,
        "addresses": addresses,
        "cart_source": cart_source,
    })


def cart_add(request):
    if request.method != "POST":
        return redirect("home")

    product = get_object_or_404(
        Product.objects.select_related("restaurant_ref"),
        id=request.POST.get("product_id"),
        is_available=True,
    )
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, 20))

    cart = _cart(request)
    conflict = _cart_source_conflict(cart, product)
    if conflict:
        messages.error(
            request,
            f"This cart only accepts items from {_source_label(conflict)}. "
            f"Place that order or clear the cart before adding food from {_source_label(product)}.",
        )
        return redirect("cart_detail")

    product_id = str(product.id)
    cart[product_id] = min(cart.get(product_id, 0) + quantity, 20)
    _save_cart(request, cart)
    return redirect("cart_detail")


def cart_update(request):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = _cart(request)
    product_id = request.POST.get("product_id")
    try:
        quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        quantity = 0

    if product_id in cart:
        if request.POST.get("remove"):
            quantity = 0
        if quantity > 0:
            cart[product_id] = quantity
        else:
            del cart[product_id]
        _save_cart(request, cart)
    return redirect("cart_detail")


def cart_clear(request):
    if request.method == "POST":
        _save_cart(request, {})
    return redirect("cart_detail")


@login_required
def cart_checkout(request):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = _cart(request)
    products = Product.objects.filter(id__in=cart.keys(), is_available=True).select_related(
        "restaurant_ref"
    )
    if not products:
        return redirect("cart_detail")
    sources = {_source_key(product) for product in products}
    if len(sources) > 1:
        messages.error(
            request,
            "A cart can only contain items from one restaurant or kitchen. "
            "Remove extra items or clear the cart, then order separately.",
        )
        return redirect("cart_detail")

    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={"phone": "", "address": ""},
    )
    delivery_address = DeliveryAddress.objects.filter(
        id=request.POST.get("delivery_address"),
        customer=customer,
    ).first()
    if not delivery_address:
        messages.error(request, "Please select a delivery address before placing the order.")
        return redirect("cart_detail")

    items_total = sum(
        (product.price * cart[str(product.id)] for product in products),
        Decimal("0.00"),
    )
    delivery_fee = (
        Decimal("0.00")
        if items_total >= FREE_DELIVERY_THRESHOLD
        else DELIVERY_FEE
    )
    address_snapshot = (
        f"{delivery_address.recipient_name}\n"
        f"{delivery_address.phone}\n"
        f"{delivery_address.address_line}\n"
        f"{delivery_address.city}, {delivery_address.state} - "
        f"{delivery_address.postal_code}"
    )
    with transaction.atomic():
        order = Order.objects.create(
            customer=request.user,
            delivery_address=delivery_address,
            delivery_address_snapshot=address_snapshot,
            delivery_fee=delivery_fee,
            payment_successful=True,
        )
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart[str(product.id)],
                unit_price=product.price,
            )

    _save_cart(request, {})
    return redirect("order_detail", id=order.id)


# CREATE ORDER
@login_required
def order_create(request):
    # Orders are created only through the cart checkout, where a saved
    # delivery address and the final total are confirmed.
    return redirect("cart_detail")


def _order_for_user(request, id):
    orders = Order.objects.all()
    if not request.user.is_superuser:
        orders = orders.filter(customer=request.user)
    return get_object_or_404(orders, id=id)


# READ - ALL ORDERS
@login_required
def order_list(request):
    if request.user.is_superuser:
        orders = Order.objects.all().order_by("-created_at")
    else:
        orders = Order.objects.filter(customer=request.user).order_by("-created_at")

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders
        }
    )


# READ - SINGLE ORDER
@login_required
def order_detail(request, id):

    order = _order_for_user(request, id)

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )


# UPDATE ORDER
@login_required
def order_update(request, id):

    order = _order_for_user(request, id)

    if request.method == "POST":
        order.save()

        # Remove old items
        order.items.all().delete()

        # Add updated items
        product_ids = request.POST.getlist(
            "product"
        )

        quantities = request.POST.getlist(
            "quantity"
        )

        for product_id, quantity in zip(
            product_ids,
            quantities
        ):

            if product_id and quantity:

                product = get_object_or_404(
                    Product,
                    id=product_id
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=int(quantity),
                    unit_price=product.price,
                )

        return redirect(
            "order_detail",
            id=order.id
        )

    customers = User.objects.all()

    products = Product.objects.filter(
        is_available=True
    )

    return render(
        request,
        "orders/order_form.html",
        {
            "order": order,
            "customers": customers,
            "products": products
        }
    )


# DELETE ORDER
@login_required
def order_delete(request, id):

    order = _order_for_user(request, id)

    if request.method == "POST":

        order.delete()

        return redirect(
            "order_list"
        )

    return render(
        request,
        "orders/order_confirm_delete.html",
        {
            "order": order
        }
    )


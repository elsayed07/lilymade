from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction

from catalog.models import ProductVariant
from catalog.pricing import convert_from_eur, normalize_currency

from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY

# Countries the store ships to (Europe + a few others), for Stripe address collection.
SHIP_COUNTRIES = [
    "IT", "FR", "DE", "ES", "PT", "NL", "BE", "AT", "IE", "GR", "FI", "SE", "DK",
    "PL", "CZ", "SK", "HU", "RO", "HR", "SI", "LU", "EE", "LV", "LT", "BG",
    "GB", "CH", "NO", "US", "CA", "AU",
]


class CheckoutError(Exception):
    pass


def _to_minor(amount):
    return int((Decimal(amount) * 100).to_integral_value())


def create_checkout_session(items_input, currency, user=None):
    currency = normalize_currency(currency)
    if not items_input:
        raise CheckoutError("Cart is empty.")

    line_items = []
    order_items = []
    subtotal_eur = Decimal("0")

    for entry in items_input:
        variant_id = entry.get("variant_id")
        try:
            qty = int(entry.get("quantity", 1))
        except (TypeError, ValueError):
            raise CheckoutError("Invalid quantity.")
        if qty < 1:
            raise CheckoutError("Invalid quantity.")
        try:
            variant = ProductVariant.objects.select_related("product").get(
                pk=variant_id, product__status="active"
            )
        except ProductVariant.DoesNotExist:
            raise CheckoutError(f"Product variant {variant_id} is not available.")
        if variant.inventory_quantity < qty:
            raise CheckoutError(
                f"'{variant.product.title} – {variant.title}' does not have enough stock."
            )

        unit_price = convert_from_eur(variant.price_eur, currency)
        subtotal_eur += variant.price_eur * qty
        line_items.append(
            {
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {"name": f"{variant.product.title} – {variant.title}"},
                    "unit_amount": _to_minor(unit_price),
                },
                "quantity": qty,
            }
        )
        order_items.append((variant, unit_price, qty))

    free = subtotal_eur >= settings.FREE_SHIPPING_THRESHOLD_EUR
    shipping_eur = Decimal("0") if free else Decimal(str(settings.SHIPPING_FLAT_RATE_EUR))
    shipping_amount = convert_from_eur(shipping_eur, currency)

    shipping_options = [
        {
            "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {
                    "amount": _to_minor(shipping_amount),
                    "currency": currency.lower(),
                },
                "display_name": "Free shipping" if free else "Standard shipping",
            }
        }
    ]

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        shipping_options=shipping_options,
        shipping_address_collection={"allowed_countries": SHIP_COUNTRIES},
        customer_email=(user.email if (user and user.is_authenticated and user.email) else None),
        success_url=f"{settings.FRONTEND_URL}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/cart",
    )

    subtotal_cur = convert_from_eur(subtotal_eur, currency)
    order = Order.objects.create(
        user=user if (user and user.is_authenticated) else None,
        email=user.email if (user and user.is_authenticated) else "",
        status="pending",
        currency=currency,
        subtotal=subtotal_cur,
        shipping=shipping_amount,
        total=subtotal_cur + shipping_amount,
        stripe_session_id=session.id,
    )
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                variant=variant,
                product_title=variant.product.title,
                variant_title=variant.title,
                unit_price=unit_price,
                currency=currency,
                quantity=qty,
            )
            for variant, unit_price, qty in order_items
        ]
    )
    return session


def fulfill_order(session):
    """Idempotently mark a pending order paid and decrement inventory."""
    session_id = session.get("id")
    if not Order.objects.filter(stripe_session_id=session_id).exists():
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().get(stripe_session_id=session_id)
        if order.status == "paid":
            return
        for item in order.items.all():
            if item.variant_id:
                variant = ProductVariant.objects.select_for_update().get(pk=item.variant_id)
                variant.inventory_quantity = max(variant.inventory_quantity - item.quantity, 0)
                variant.save(update_fields=["inventory_quantity"])

        details = session.get("customer_details") or {}
        if details.get("email"):
            order.email = details["email"]
        shipping = session.get("shipping_details") or {}
        order.shipping_address = shipping or {"address": details.get("address")}
        order.stripe_payment_intent = session.get("payment_intent") or ""
        order.status = "paid"
        order.save()

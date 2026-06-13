import time
from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction

from catalog.models import ProductVariant
from catalog.pricing import convert_from_eur, normalize_currency

from .emails import send_dispute_alert, send_order_emails
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


def _parse_items(items_input):
    """Validate the raw cart payload into (variant_id, qty) pairs. No DB access."""
    parsed = []
    for entry in items_input:
        variant_id = entry.get("variant_id")
        try:
            qty = int(entry.get("quantity", 1))
        except (TypeError, ValueError):
            raise CheckoutError("Invalid quantity.")
        if qty < 1:
            raise CheckoutError("Invalid quantity.")
        parsed.append((variant_id, qty))
    return parsed


def create_checkout_session(items_input, currency, user=None):
    """Reserve stock, create a pending order, then open a Stripe Checkout session.

    Inventory is decremented (reserved) inside a row-locked transaction at checkout so
    two buyers can never pay for the same one-of-a-kind item. If the customer never
    pays, Stripe expires the session and `expire_order` releases the reservation.
    """
    currency = normalize_currency(currency)
    if not items_input:
        raise CheckoutError("Cart is empty.")
    parsed = _parse_items(items_input)

    # Reserve stock + create the pending order atomically.
    with transaction.atomic():
        line_items = []
        order_items = []
        subtotal_eur = Decimal("0")
        for variant_id, qty in parsed:
            try:
                variant = (
                    ProductVariant.objects.select_for_update()
                    .select_related("product")
                    .get(pk=variant_id, product__status="active")
                )
            except ProductVariant.DoesNotExist:
                raise CheckoutError(f"Product variant {variant_id} is not available.")
            if variant.inventory_quantity < qty:
                raise CheckoutError(
                    f"'{variant.product.title} – {variant.title}' does not have enough stock."
                )
            variant.inventory_quantity -= qty  # reserve
            variant.save(update_fields=["inventory_quantity"])

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
        subtotal_cur = convert_from_eur(subtotal_eur, currency)

        order = Order.objects.create(
            user=user if (user and user.is_authenticated) else None,
            email=user.email if (user and user.is_authenticated and user.email) else "",
            status="pending",
            currency=currency,
            subtotal=subtotal_cur,
            shipping=shipping_amount,
            total=subtotal_cur + shipping_amount,
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

    # Stripe network call is outside the DB lock; release the reservation if it fails.
    try:
        kwargs = {
            "mode": "payment",
            "line_items": line_items,
            "shipping_options": shipping_options,
            "shipping_address_collection": {"allowed_countries": SHIP_COUNTRIES},
            "allow_promotion_codes": True,
            "expires_at": int(time.time()) + settings.CHECKOUT_SESSION_TTL_MINUTES * 60,
            "customer_email": (order.email or None),
            "success_url": f"{settings.FRONTEND_URL}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{settings.FRONTEND_URL}/cart",
            "metadata": {"order_id": str(order.pk)},
        }
        if settings.STRIPE_AUTOMATIC_TAX:
            kwargs["automatic_tax"] = {"enabled": True}
        session = stripe.checkout.Session.create(**kwargs)
    except Exception:
        expire_order(order)  # give the stock back
        raise

    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id"])
    return session


def fulfill_order(session):
    """Idempotently mark a pending order paid. Stock was already reserved at checkout."""
    session_id = session.get("id")
    order = Order.objects.filter(stripe_session_id=session_id).first()
    if order is None:
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status in ("paid", "fulfilled", "refunded"):
            return
        details = session.get("customer_details") or {}
        if details.get("email"):
            order.email = details["email"]
        shipping = session.get("shipping_details") or {}
        order.shipping_address = shipping or {"address": details.get("address")}
        order.stripe_payment_intent = session.get("payment_intent") or ""
        order.status = "paid"
        order.save()

    send_order_emails(order)


def expire_order(order):
    """Release reserved stock for an unpaid order and cancel it (idempotent)."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status != "pending":
            return
        _restock(order)
        order.status = "cancelled"
        order.save(update_fields=["status"])


def expire_order_by_session(session):
    session_id = session.get("id")
    order = Order.objects.filter(stripe_session_id=session_id).first()
    if order is not None:
        expire_order(order)


def handle_refund(payment_intent_id):
    """Mark a paid order refunded and return its items to stock (handmade = resellable)."""
    if not payment_intent_id:
        return
    order = Order.objects.filter(stripe_payment_intent=payment_intent_id).first()
    if order is None:
        return
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status == "refunded":
            return
        _restock(order)
        order.status = "refunded"
        order.save(update_fields=["status"])


def handle_dispute(payment_intent_id):
    """A chargeback was opened — alert the seller so they can respond in Stripe."""
    order = Order.objects.filter(stripe_payment_intent=payment_intent_id).first()
    if order is not None:
        send_dispute_alert(order)


def _restock(order):
    for item in order.items.all():
        if item.variant_id:
            variant = ProductVariant.objects.select_for_update().get(pk=item.variant_id)
            variant.inventory_quantity += item.quantity
            variant.save(update_fields=["inventory_quantity"])

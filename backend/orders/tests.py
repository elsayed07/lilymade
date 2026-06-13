from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings

from catalog.models import CurrencyRate, Product, ProductVariant
from orders.models import Order
from orders.services import (
    CheckoutError,
    create_checkout_session,
    expire_order,
    fulfill_order,
    handle_refund,
)

FAKE_SESSION = SimpleNamespace(id="cs_test_123", url="https://checkout.stripe.test/cs_test_123")


def fake_session_payload(session_id="cs_test_123", email="buyer@example.com"):
    return {
        "id": session_id,
        "customer_details": {"email": email},
        "shipping_details": {"address": {"city": "Rome"}},
        "payment_intent": "pi_test_123",
    }


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Lilymade <no-reply@lilymade.it>",
    ORDER_NOTIFICATION_EMAIL="seller@lilymade.it",
    FREE_SHIPPING_THRESHOLD_EUR=100,
    SHIPPING_FLAT_RATE_EUR=7,
)
class CheckoutTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(handle="bag", title="Bag", status="active")
        self.variant = ProductVariant.objects.create(
            product=self.product, title="Black", price_eur=Decimal("65.00"), inventory_quantity=1
        )

    def _checkout(self, qty=1, currency="EUR"):
        return create_checkout_session(
            [{"variant_id": self.variant.id, "quantity": qty}], currency
        )

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_checkout_reserves_inventory(self, _create):
        self._checkout()
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.inventory_quantity, 0)  # reserved
        order = Order.objects.get(stripe_session_id="cs_test_123")
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.total, Decimal("72.00"))  # 65 + 7 shipping

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_second_buyer_cannot_oversell(self, _create):
        self._checkout()  # reserves the only unit
        with self.assertRaises(CheckoutError):
            self._checkout()  # no stock left
        self.assertEqual(Order.objects.filter(status="pending").count(), 1)

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_fulfill_is_idempotent_and_does_not_double_decrement(self, _create):
        self._checkout()
        fulfill_order(fake_session_payload())
        fulfill_order(fake_session_payload())  # webhook retry
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.inventory_quantity, 0)  # not -1
        order = Order.objects.get(stripe_session_id="cs_test_123")
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.email, "buyer@example.com")
        # Confirmation to customer + notification to seller.
        self.assertEqual(len(mail.outbox), 2)

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_expire_releases_reservation(self, _create):
        self._checkout()
        order = Order.objects.get(stripe_session_id="cs_test_123")
        expire_order(order)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.inventory_quantity, 1)  # back in stock
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_refund_restocks_and_marks_refunded(self, _create):
        self._checkout()
        fulfill_order(fake_session_payload())
        handle_refund("pi_test_123")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.inventory_quantity, 1)
        self.assertEqual(Order.objects.get(stripe_payment_intent="pi_test_123").status, "refunded")

    @mock.patch("orders.services.stripe.checkout.Session.create", return_value=FAKE_SESSION)
    def test_currency_conversion_applied_to_totals(self, _create):
        CurrencyRate.objects.create(
            code="USD", symbol="$", rate_to_eur=Decimal("1.10"), active=True
        )
        self._checkout(currency="USD")
        order = Order.objects.get(stripe_session_id="cs_test_123")
        self.assertEqual(order.currency, "USD")
        # 65 * 1.10 = 71.50 subtotal, 7 * 1.10 = 7.70 shipping
        self.assertEqual(order.subtotal, Decimal("71.50"))
        self.assertEqual(order.shipping, Decimal("7.70"))

    def test_stripe_failure_releases_reservation(self):
        with mock.patch(
            "orders.services.stripe.checkout.Session.create",
            side_effect=RuntimeError("stripe down"),
        ):
            with self.assertRaises(RuntimeError):
                self._checkout()
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.inventory_quantity, 1)  # rolled back

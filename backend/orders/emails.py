"""Transactional email for orders. All sends are best-effort (fail_silently):
payment has already succeeded by the time these run, so an SMTP hiccup must never
raise back into the webhook handler."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _ctx(order):
    return {
        "order": order,
        "items": list(order.items.all()),
        "site": settings.FRONTEND_URL,
    }


def send_order_emails(order):
    """Confirmation to the customer + new-order notification to the seller."""
    ctx = _ctx(order)
    if order.email:
        try:
            body = render_to_string("orders/email/order_confirmation.txt", ctx)
            EmailMessage(
                subject=f"Lilymade — order confirmation #{order.pk}",
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.email],
            ).send(fail_silently=True)
        except Exception:  # noqa: BLE001 - never break fulfillment on email
            logger.exception("Failed to send order confirmation for #%s", order.pk)

    if settings.ORDER_NOTIFICATION_EMAIL:
        try:
            body = render_to_string("orders/email/seller_notification.txt", ctx)
            EmailMessage(
                subject=f"New order #{order.pk} — {order.total} {order.currency}",
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.ORDER_NOTIFICATION_EMAIL],
            ).send(fail_silently=True)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to send seller notification for #%s", order.pk)


def send_dispute_alert(order):
    if not settings.ORDER_NOTIFICATION_EMAIL:
        return
    try:
        EmailMessage(
            subject=f"⚠ Dispute opened on order #{order.pk}",
            body=(
                f"A payment dispute/chargeback was opened on order #{order.pk} "
                f"({order.total} {order.currency}, {order.email}).\n\n"
                "Respond in your Stripe Dashboard → Payments → Disputes before the deadline."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ORDER_NOTIFICATION_EMAIL],
        ).send(fail_silently=True)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send dispute alert for #%s", order.pk)

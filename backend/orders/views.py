import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer
from .services import (
    CheckoutError,
    create_checkout_session,
    expire_order_by_session,
    fulfill_order,
    handle_dispute,
    handle_refund,
)


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "checkout"

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {"detail": "Payments are not configured yet. Add a Stripe secret key."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        items = request.data.get("items", [])
        currency = request.data.get("currency", "EUR")
        user = request.user if request.user.is_authenticated else None
        try:
            session = create_checkout_session(items, currency, user)
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.StripeError:
            return Response(
                {"detail": "Payment provider error. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"url": session.url, "id": session.id})


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderBySessionView(generics.RetrieveAPIView):
    """Look up an order by its (unguessable) Stripe session id for the success page."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        session_id = self.kwargs["session_id"]
        order = (
            Order.objects.filter(stripe_session_id=session_id)
            .prefetch_related("items")
            .first()
        )
        if order is None:
            raise NotFound("Order not found.")
        return order


# Stripe webhook event -> handler.
WEBHOOK_HANDLERS = {
    "checkout.session.completed": lambda obj: fulfill_order(obj),
    "checkout.session.expired": lambda obj: expire_order_by_session(obj),
    "charge.refunded": lambda obj: handle_refund(obj.get("payment_intent")),
    "charge.dispute.created": lambda obj: handle_dispute(obj.get("payment_intent")),
}


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)
    handler = WEBHOOK_HANDLERS.get(event["type"])
    if handler:
        handler(event["data"]["object"])
    return HttpResponse(status=200)

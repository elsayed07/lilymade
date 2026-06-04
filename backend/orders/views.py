import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer
from .services import CheckoutError, create_checkout_session, fulfill_order


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

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
    if event["type"] == "checkout.session.completed":
        fulfill_order(event["data"]["object"])
    return HttpResponse(status=200)

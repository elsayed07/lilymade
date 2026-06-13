from django.urls import path

from .views import (
    CheckoutView,
    OrderBySessionView,
    OrderHistoryView,
    stripe_webhook,
)

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    path("account/orders/", OrderHistoryView.as_view(), name="order-history"),
    path("orders/session/<str:session_id>/", OrderBySessionView.as_view(), name="order-by-session"),
]

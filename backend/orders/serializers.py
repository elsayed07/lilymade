from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product_title", "variant_title", "unit_price", "currency", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "email",
            "status",
            "currency",
            "subtotal",
            "shipping",
            "total",
            "created_at",
            "items",
        )

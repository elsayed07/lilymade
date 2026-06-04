from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "variant",
        "product_title",
        "variant_title",
        "unit_price",
        "currency",
        "quantity",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "currency", "total", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("email", "stripe_session_id", "stripe_payment_intent")
    readonly_fields = ("stripe_session_id", "stripe_payment_intent", "created_at")
    inlines = [OrderItemInline]

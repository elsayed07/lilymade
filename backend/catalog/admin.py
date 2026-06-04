from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Collection, CurrencyRate, Product, ProductImage, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Collection)
class CollectionAdmin(TranslationAdmin):
    list_display = ("title", "handle", "position")
    search_fields = ("title", "handle")


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ("title", "status", "product_type", "created_at")
    list_filter = ("status", "collections")
    search_fields = ("title", "handle")
    filter_horizontal = ("collections",)
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("__str__", "price_eur", "inventory_quantity")
    list_editable = ("price_eur", "inventory_quantity")
    search_fields = ("product__title", "title")


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ("code", "symbol", "rate_to_eur", "active")
    list_editable = ("symbol", "rate_to_eur", "active")

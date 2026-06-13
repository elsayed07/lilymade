from rest_framework import serializers

from .models import Collection, Product, ProductImage, ProductVariant
from .pricing import convert_from_eur


def image_url(file_field, fallback, request):
    """Absolute URL of a self-hosted image, falling back to a stored remote URL."""
    if file_field:
        url = file_field.url
        return request.build_absolute_uri(url) if request is not None else url
    return fallback or None


class VariantSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ("id", "title", "price", "currency", "in_stock", "inventory_quantity")

    def _currency(self):
        return self.context.get("currency", "EUR")

    def get_currency(self, obj):
        return self._currency()

    def get_price(self, obj):
        return str(convert_from_eur(obj.price_eur, self._currency(), self.context.get("rates")))


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("url", "alt", "position")

    def get_url(self, obj):
        return image_url(obj.image, obj.url, self.context.get("request"))


class ProductListSerializer(serializers.ModelSerializer):
    price_from = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "handle", "title", "price_from", "currency", "featured_image", "in_stock")

    def _currency(self):
        return self.context.get("currency", "EUR")

    def get_currency(self, obj):
        return self._currency()

    def get_price_from(self, obj):
        prices = [v.price_eur for v in obj.variants.all()]
        if not prices:
            return None
        return str(convert_from_eur(min(prices), self._currency(), self.context.get("rates")))

    def get_featured_image(self, obj):
        image = obj.images.all().first()
        if not image:
            return None
        return image_url(image.image, image.url, self.context.get("request"))

    def get_in_stock(self, obj):
        return any(v.inventory_quantity > 0 for v in obj.variants.all())


class ProductDetailSerializer(ProductListSerializer):
    images = ImageSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    collections = serializers.SlugRelatedField(slug_field="handle", many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description",
            "product_type",
            "tags",
            "images",
            "variants",
            "collections",
        )


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ("handle", "title", "description", "image", "products_count")

    def get_products_count(self, obj):
        return obj.products.filter(status="active").count()

    def get_image(self, obj):
        return image_url(obj.image_file, obj.image, self.context.get("request"))


class CollectionDetailSerializer(CollectionSerializer):
    products = serializers.SerializerMethodField()

    class Meta(CollectionSerializer.Meta):
        fields = CollectionSerializer.Meta.fields + ("products",)

    def get_products(self, obj):
        qs = obj.products.filter(status="active").prefetch_related("variants", "images")
        return ProductListSerializer(qs, many=True, context=self.context).data

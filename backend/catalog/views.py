from django.conf import settings
from django.utils import translation
from rest_framework import generics

from .models import Collection, Product
from .pricing import get_currency_rates, normalize_currency
from .serializers import (
    CollectionDetailSerializer,
    CollectionSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class StorefrontMixin:
    """Activates the requested language and injects currency context."""

    def initial(self, request, *args, **kwargs):
        lang = request.query_params.get("lang")
        if lang in dict(settings.LANGUAGES):
            translation.activate(lang)
        super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["currency"] = normalize_currency(self.request.query_params.get("currency"))
        ctx["rates"] = get_currency_rates()
        return ctx


class ProductListView(StorefrontMixin, generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(status="active").prefetch_related(
            "variants", "images", "collections"
        )
        collection = self.request.query_params.get("collection")
        if collection:
            qs = qs.filter(collections__handle=collection)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.distinct()


class ProductDetailView(StorefrontMixin, generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "handle"

    def get_queryset(self):
        return Product.objects.filter(status="active").prefetch_related(
            "variants", "images", "collections"
        )


class CollectionListView(StorefrontMixin, generics.ListAPIView):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()


class CollectionDetailView(StorefrontMixin, generics.RetrieveAPIView):
    serializer_class = CollectionDetailSerializer
    lookup_field = "handle"
    queryset = Collection.objects.all()

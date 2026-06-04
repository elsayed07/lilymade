from django.urls import path

from .views import (
    CollectionDetailView,
    CollectionListView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:handle>/", ProductDetailView.as_view(), name="product-detail"),
    path("collections/", CollectionListView.as_view(), name="collection-list"),
    path("collections/<slug:handle>/", CollectionDetailView.as_view(), name="collection-detail"),
]

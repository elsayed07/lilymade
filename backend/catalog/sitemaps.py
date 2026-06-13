"""Sitemaps for the storefront. Locations are SPA routes (served same-origin),
so search engines crawl the React URLs, not the API ones."""

from django.contrib.sitemaps import Sitemap

from .models import Collection, Product


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(status="active")

    def location(self, obj):
        return f"/products/{obj.handle}"

    def lastmod(self, obj):
        return obj.created_at


class CollectionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Collection.objects.all()

    def location(self, obj):
        return f"/collections/{obj.handle}"


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["/", "/shop", "/about", "/contact", "/policies"]

    def location(self, item):
        return item


SITEMAPS = {
    "products": ProductSitemap,
    "collections": CollectionSitemap,
    "static": StaticSitemap,
}

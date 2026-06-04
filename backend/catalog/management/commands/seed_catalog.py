"""Seed the catalog from the live Shopify store's public JSON endpoints.

Pulls products, variants, images and collections from
https://lily-20250294.myshopify.com so the new store starts with real data.
Inventory is approximate (the public API only exposes an availability flag);
exact stock is managed afterwards in the Django admin.
"""

import html
import re
from decimal import Decimal

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import (
    Collection,
    CurrencyRate,
    Product,
    ProductImage,
    ProductVariant,
)

DEFAULT_STORE = "https://lily-20250294.myshopify.com"

CURRENCY_RATES = [
    # 1 EUR = rate of this currency (approximate; editable in admin)
    {"code": "USD", "symbol": "$", "rate_to_eur": Decimal("1.08")},
    {"code": "GBP", "symbol": "£", "rate_to_eur": Decimal("0.85")},
    {"code": "CAD", "symbol": "CA$", "rate_to_eur": Decimal("1.48")},
]


def strip_html(raw):
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


class Command(BaseCommand):
    help = "Import products, variants, images and collections from the Shopify store."

    def add_arguments(self, parser):
        parser.add_argument("--store", default=DEFAULT_STORE)
        parser.add_argument(
            "--default-stock",
            type=int,
            default=1,
            help="Inventory assigned to available variants (handmade items are mostly one-off).",
        )

    def handle(self, *args, **options):
        store = options["store"].rstrip("/")
        default_stock = options["default_stock"]

        with transaction.atomic():
            self._seed_currencies()
            handle_to_product = self._seed_products(store, default_stock)
            self._seed_collections(store, handle_to_product)

        self.stdout.write(self.style.SUCCESS(
            f"Done. {Product.objects.count()} products, "
            f"{ProductVariant.objects.count()} variants, "
            f"{Collection.objects.count()} collections."
        ))

    def _seed_currencies(self):
        for row in CURRENCY_RATES:
            CurrencyRate.objects.update_or_create(
                code=row["code"],
                defaults={"symbol": row["symbol"], "rate_to_eur": row["rate_to_eur"], "active": True},
            )

    def _seed_products(self, store, default_stock):
        products = self._fetch_all(f"{store}/products.json", "products")
        handle_to_product = {}
        for p in products:
            product, _ = Product.objects.update_or_create(
                handle=p["handle"],
                defaults={
                    "title": p["title"],
                    "description": strip_html(p.get("body_html")),
                    "product_type": p.get("product_type", "") or "",
                    "tags": p.get("tags", []) or [],
                    "status": "active",
                },
            )
            product.images.all().delete()
            for img in p.get("images", []):
                ProductImage.objects.create(
                    product=product,
                    url=img["src"],
                    alt=(img.get("alt") or product.title),
                    position=img.get("position", 0),
                )
            product.variants.all().delete()
            for v in p.get("variants", []):
                opts = [v.get("option1"), v.get("option2"), v.get("option3")]
                title = " / ".join(o for o in opts if o) or "Default"
                ProductVariant.objects.create(
                    product=product,
                    title=title,
                    price_eur=Decimal(str(v["price"])),
                    inventory_quantity=default_stock if v.get("available") else 0,
                    position=v.get("position", 0),
                )
            handle_to_product[p["handle"]] = product
            self.stdout.write(f"  product: {product.title}")
        return handle_to_product

    def _seed_collections(self, store, handle_to_product):
        collections = self._fetch_all(f"{store}/collections.json", "collections")
        for idx, c in enumerate(collections):
            collection, _ = Collection.objects.update_or_create(
                handle=c["handle"],
                defaults={
                    "title": c["title"],
                    "description": strip_html(c.get("body_html")),
                    "image": (c.get("image") or {}).get("src", "") if c.get("image") else "",
                    "position": idx,
                },
            )
            members = self._fetch_all(
                f"{store}/collections/{c['handle']}/products.json", "products"
            )
            collection.products.clear()
            for m in members:
                product = handle_to_product.get(m["handle"])
                if product:
                    collection.products.add(product)
            self.stdout.write(f"  collection: {collection.title} ({collection.products.count()})")

    def _fetch_all(self, url, key):
        """Fetch a Shopify public JSON listing, paginating until empty."""
        results = []
        page = 1
        while True:
            resp = requests.get(url, params={"limit": 250, "page": page}, timeout=30)
            resp.raise_for_status()
            batch = resp.json().get(key, [])
            if not batch:
                break
            results.extend(batch)
            if len(batch) < 250:
                break
            page += 1
        return results

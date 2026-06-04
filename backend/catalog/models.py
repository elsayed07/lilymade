from django.db import models
from django.utils import timezone


class Collection(models.Model):
    handle = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.title


class Product(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("draft", "Draft"),
        ("archived", "Archived"),
    ]
    handle = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    collections = models.ManyToManyField(Collection, related_name="products", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField(max_length=500)
    alt = models.CharField(max_length=200, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default="Default")
    price_eur = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_quantity = models.PositiveIntegerField(default=0)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.product.title} – {self.title}"

    @property
    def in_stock(self):
        return self.inventory_quantity > 0


class CurrencyRate(models.Model):
    code = models.CharField(max_length=3, unique=True)
    symbol = models.CharField(max_length=5)
    rate_to_eur = models.DecimalField(
        max_digits=12, decimal_places=6, help_text="1 EUR = X of this currency"
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

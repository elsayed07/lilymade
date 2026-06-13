import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory

from .models import Collection, Product, ProductImage
from .serializers import (
    CollectionSerializer,
    ImageSerializer,
    ProductListSerializer,
)

MEDIA_ROOT = tempfile.mkdtemp()

# A minimal valid 1x1 PNG.
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
    "de0000000c4944415408d76360000002000154a24f1e0000000049454e44ae426082"
)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SelfHostedImageTests(TestCase):
    """Images imported from Shopify must be served from our own /media/, not a remote CDN."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.request = APIRequestFactory().get("/api/products/")

    def _png(self, name="bag.png"):
        return SimpleUploadedFile(name, PNG_BYTES, content_type="image/png")

    def test_product_image_url_is_self_hosted(self):
        product = Product.objects.create(handle="bag", title="Bag")
        image = ProductImage.objects.create(
            product=product,
            image=self._png(),
            url="https://cdn.shopify.com/old.jpg",
        )
        url = ImageSerializer(image, context={"request": self.request}).data["url"]
        self.assertIn("/media/products/", url)
        self.assertNotIn("cdn.shopify.com", url)
        self.assertTrue(url.startswith("http"))  # absolute

    def test_falls_back_to_remote_url_without_local_file(self):
        product = Product.objects.create(handle="bag2", title="Bag 2")
        image = ProductImage.objects.create(
            product=product, url="https://cdn.shopify.com/legacy.jpg"
        )
        url = ImageSerializer(image, context={"request": self.request}).data["url"]
        self.assertEqual(url, "https://cdn.shopify.com/legacy.jpg")

    def test_featured_image_prefers_local_file(self):
        product = Product.objects.create(handle="bag3", title="Bag 3")
        ProductImage.objects.create(
            product=product, image=self._png(), url="https://cdn.shopify.com/x.jpg"
        )
        data = ProductListSerializer(product, context={"request": self.request}).data
        self.assertIn("/media/products/", data["featured_image"])

    def test_collection_image_is_self_hosted(self):
        collection = Collection.objects.create(
            handle="totes",
            title="Totes",
            image_file=self._png("totes.png"),
            image="https://cdn.shopify.com/coll.jpg",
        )
        url = CollectionSerializer(collection, context={"request": self.request}).data["image"]
        self.assertIn("/media/collections/", url)
        self.assertNotIn("cdn.shopify.com", url)

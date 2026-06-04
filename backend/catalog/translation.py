from modeltranslation.translator import TranslationOptions, register

from .models import Collection, Product


@register(Collection)
class CollectionTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("title", "description")

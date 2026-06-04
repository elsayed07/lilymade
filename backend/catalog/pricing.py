from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from .models import CurrencyRate

CENTS = Decimal("0.01")


def normalize_currency(currency):
    currency = (currency or settings.BASE_CURRENCY).upper()
    if currency not in settings.SUPPORTED_CURRENCIES:
        return settings.BASE_CURRENCY
    return currency


def get_currency_rates():
    rates = {settings.BASE_CURRENCY: Decimal("1")}
    for rate in CurrencyRate.objects.filter(active=True):
        rates[rate.code] = rate.rate_to_eur
    return rates


def convert_from_eur(amount_eur, currency, rates=None):
    currency = normalize_currency(currency)
    if rates is None:
        rates = get_currency_rates()
    rate = rates.get(currency, Decimal("1"))
    return (Decimal(amount_eur) * rate).quantize(CENTS, rounding=ROUND_HALF_UP)

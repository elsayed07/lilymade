"""Release inventory reserved by pending orders that were never paid.

The Stripe `checkout.session.expired` webhook normally frees reserved stock, but this
command is a safety net (run it on a schedule, e.g. hourly cron) in case a webhook is
missed. It only touches orders older than the checkout TTL, so live sessions are safe.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order
from orders.services import expire_order


class Command(BaseCommand):
    help = "Cancel stale pending orders and return their reserved stock."

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-minutes",
            type=int,
            default=settings.CHECKOUT_SESSION_TTL_MINUTES + 30,
            help="Only release pending orders older than this (default: TTL + 30 min).",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=options["older_than_minutes"])
        stale = Order.objects.filter(status="pending", created_at__lt=cutoff)
        count = 0
        for order in stale:
            expire_order(order)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Released {count} stale pending order(s)."))

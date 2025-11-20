from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notices.models import Notice

class Command(BaseCommand):
    help = "Auto delete notices after 5 minutes"

    def handle(self, *args, **options):
        now = timezone.now()
        five_minutes_ago = now - timedelta(minutes=5)

        deleted = Notice.objects.filter(
            created_at__lt=five_minutes_ago
        ).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Auto delete completed. Deleted notices: {deleted[0]}"
        ))

import os

from django.conf import settings
from django.core.management import BaseCommand

TEST_CERT = os.path.join(settings.BASE_DIR, "certs", "fullchain.pem",)


class Command(BaseCommand):
    def handle(self, **options):
        import bpdb

        bpdb.set_trace()

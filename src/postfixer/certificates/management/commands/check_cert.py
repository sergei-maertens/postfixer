import os

from django.conf import settings
from django.core.management import BaseCommand

from ... import ensure_certificate_up_to_date

TEST_CERT = os.path.join(settings.BASE_DIR, "certs", "fullchain.pem",)

MAIL_HOSTS = [
    "pi-modelling.nl",
    "modelbrouwers.nl",
]


class Command(BaseCommand):
    def handle(self, **options):
        ensure_certificate_up_to_date(TEST_CERT, MAIL_HOSTS)

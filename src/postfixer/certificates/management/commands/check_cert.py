import os

from django.conf import settings
from django.core.management import BaseCommand

from ...utils import get_certificate_domains

TEST_CERT = os.path.join(settings.BASE_DIR, "certs", "fullchain.pem",)

HOST = "pi-modelling.nl"

MAIL_HOSTS = [
    "pi-modelling.nl",
    "modelbrouwers.nl",
]


class Command(BaseCommand):
    def handle(self, **options):
        generate, domains = get_certificate_domains(TEST_CERT, MAIL_HOSTS)
        print(generate, domains)

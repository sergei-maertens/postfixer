import os

from django.conf import settings
from django.core.management import BaseCommand

from ...utils import extract_domains

TEST_CERT = os.path.join(settings.BASE_DIR, "certs", "fullchain.pem",)


class Command(BaseCommand):
    def handle(self, **options):
        domains = extract_domains(TEST_CERT)
        self.stdout.write("Domains: ")
        for domain in domains:
            self.stdout.write(f"- {domain}")

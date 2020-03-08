import os

from django.conf import settings
from django.core.management import BaseCommand

from ...utils import extract_domains, get_relevant_mx_hosts

TEST_CERT = os.path.join(settings.BASE_DIR, "certs", "fullchain.pem",)

HOST = "pi-modelling.nl"


class Command(BaseCommand):
    def handle(self, **options):
        domains = extract_domains(TEST_CERT)
        self.stdout.write("Domains: ")
        for domain in domains:
            self.stdout.write(f"- {domain}")

        hosts = get_relevant_mx_hosts(HOST)
        self.stdout.write(f"Relvant MX hosts for {HOST}:")
        for host in hosts:
            self.stdout.write(f"- {host[0]}: {host[1]}")

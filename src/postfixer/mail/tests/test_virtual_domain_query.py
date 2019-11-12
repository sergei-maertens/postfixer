from django.test import TestCase

from ..models import VirtualMailbox


class QueryTests(TestCase):
    def test_lookup_mailbox(self):
        VirtualMailbox.objects.create(email="info@regex-it.nl")

        maildirs = VirtualMailbox.objects.get_maildir("info@regex-it.nl")

        self.assertQuerysetEqual(
            maildirs, ["regex-it.nl/info/"], transform=lambda x: x,
        )

    def test_virtual_mailbox_domain(self):
        VirtualMailbox.objects.create(email="info@regex-it.nl")

        domains = VirtualMailbox.objects.get_domain("regex-it.nl")

        self.assertQuerysetEqual(
            domains, ["regex-it.nl"], transform=lambda x: x,
        )

from django.test import TestCase

from ..models import Forward, VirtualMailbox, get_domain


def identity(x):
    return x


class QueryTests(TestCase):
    def test_lookup_mailbox(self):
        VirtualMailbox.objects.create(email="info@regex-it.nl")

        maildirs = VirtualMailbox.objects.get_maildir("info@regex-it.nl")

        self.assertQuerysetEqual(
            maildirs, ["regex-it.nl/info/"], transform=identity,
        )

    def test_virtual_mailbox_domain(self):
        VirtualMailbox.objects.create(email="info@regex-it.nl")

        domains = VirtualMailbox.objects.get_domain("regex-it.nl")

        self.assertQuerysetEqual(
            domains, ["regex-it.nl"], transform=identity,
        )

    def test_merge_domains(self):
        Forward.objects.create(
            domain_part="regex-it.nl", user_part="info", destinations=["foo@bar.com"]
        )
        VirtualMailbox.objects.create(domain_part="xbbtx.be", user_part="info")

        qs1 = get_domain("regex-it.nl")
        qs2 = get_domain("xbbtx.be")
        qs3 = get_domain("gmail.com")

        self.assertQuerysetEqual(qs1, ["regex-it.nl"], transform=identity)
        self.assertQuerysetEqual(qs2, ["xbbtx.be"], transform=identity)
        self.assertQuerysetEqual(qs3, [], transform=identity)

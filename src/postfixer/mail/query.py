from django.db import models
from django.db.models import EmailField, Value
from django.db.models.functions import Concat


class EmailAnnotationMixin:
    def annotate_email(self):
        return self.annotate(
            email=Concat(
                "user_part", Value("@"), "domain_part", output_field=EmailField()
            )
        )

    def get_domain(self, domain: str) -> models.QuerySet:
        qs = self.filter(active=True, domain_part=domain)
        return qs.values_list("domain_part", flat=True).distinct()


class ForwardQuerySet(EmailAnnotationMixin, models.QuerySet):
    def get_forwards(self, email: str) -> models.QuerySet:
        aliases = self.annotate_email().filter(active=True, email=email)
        return aliases.values_list("destinations", flat=True)


class VirtualMailboxQuerySet(EmailAnnotationMixin, models.QuerySet):
    def get_maildir(self, email: str) -> models.QuerySet:
        mailboxes = (
            self.annotate_email()
            .annotate(
                maildir=Concat("domain_part", Value("/"), "user_part", Value("/"))
            )
            .filter(active=True, email=email)
        )
        return mailboxes.values_list("maildir", flat=True)

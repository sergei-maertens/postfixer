from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_better_admin_arrayfield.models.fields import ArrayField

from .query import ForwardQuerySet, LimitedManager, VirtualMailboxQuerySet
from .validators import validate_lowercase


class EmailPartsMixin:
    def __str__(self):
        return self.get_email()

    def __init__(self, *args, **kwargs):
        email = kwargs.pop("email", None)
        if email:
            user_part, domain_part = email.rsplit("@")
            kwargs["user_part"] = user_part
            kwargs["domain_part"] = domain_part
        super().__init__(*args, **kwargs)

    def get_email(self) -> str:
        if hasattr(self, "email"):
            return self.email
        return "@".join([self.user_part, self.domain_part])

    def set_email(self, email: str) -> None:
        self.user_part, self.domain_part = email.rsplit("@")


class Forward(EmailPartsMixin, models.Model):
    user_part = models.CharField(
        _("user part"),
        max_length=255,
        validators=[
            validate_lowercase,
            RegexValidator(regex=EmailValidator.user_regex),
        ],
    )
    domain_part = models.CharField(
        _("domain part"),
        max_length=255,
        validators=[
            validate_lowercase,
            RegexValidator(regex=EmailValidator.domain_regex),
        ],
    )
    destinations = ArrayField(models.CharField(_("destination"), max_length=320),)
    comments = models.TextField(_("comments"), blank=True)
    active = models.BooleanField(_("active"), default=True)

    objects = LimitedManager.from_queryset(ForwardQuerySet)()

    class Meta:
        verbose_name = _("forward")
        verbose_name_plural = _("forwards")
        constraints = [
            models.UniqueConstraint(
                fields=["user_part", "domain_part"], name="unique_forward_email",
            )
        ]

    def __str__(self):
        return f"{self.get_email()} -> {self.destinations}"


class VirtualMailbox(EmailPartsMixin, models.Model):
    """
    A hosted mailbox.

    See http://www.postfix.org/VIRTUAL_README.html
    """

    user_part = models.CharField(
        _("user part"),
        max_length=255,
        validators=[
            validate_lowercase,
            RegexValidator(regex=EmailValidator.user_regex),
        ],
    )
    domain_part = models.CharField(
        _("domain part"),
        max_length=255,
        validators=[
            validate_lowercase,
            RegexValidator(regex=EmailValidator.domain_regex),
        ],
    )
    password = models.CharField(_("password"), max_length=255, blank=True)
    comments = models.TextField(_("comments"), blank=True)
    active = models.BooleanField(_("active"), default=True)

    objects = LimitedManager.from_queryset(VirtualMailboxQuerySet)()

    class Meta:
        verbose_name = _("virtual mailbox")
        verbose_name_plural = _("virtual mailboxes")
        constraints = [
            models.UniqueConstraint(
                fields=["user_part", "domain_part"], name="unique_mailbox_email",
            )
        ]


def get_domain(domain: str) -> models.QuerySet:
    aliases = Forward.objects.get_domain(domain)
    mailboxes = VirtualMailbox.objects.get_domain(domain)
    return aliases.union(mailboxes)

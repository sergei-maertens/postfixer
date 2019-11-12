from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import ugettext_lazy as _

from .query import VirtualMailboxQuerySet
from .validators import validate_lowercase


class Domain(models.Model):
    name = models.CharField(_("domain name"), max_length=253, unique=True)
    comments = models.TextField(_("comments"), blank=True)
    active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    def __str__(self):
        return self.name


class Forward(models.Model):
    source = models.CharField(_("source"), max_length=320, unique=True)
    destination = models.CharField(_("destination"), max_length=320)
    comments = models.TextField(_("comments"), blank=True)
    active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("forward")
        verbose_name_plural = _("forwards")

    def __str__(self):
        return f"{self.source} -> {self.destination}"


# Virtual mailbox hosting
# https://wiki.gentoo.org/wiki/Complete_Virtual_Mail_Server/Postfix_to_Database


class VirtualMailbox(models.Model):
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

    objects = VirtualMailboxQuerySet.as_manager()

    class Meta:
        verbose_name = _("virtual mailbox")
        verbose_name_plural = _("virtual mailboxes")
        constraints = [
            models.UniqueConstraint(
                fields=["user_part", "domain_part"], name="unique_email",
            )
        ]

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

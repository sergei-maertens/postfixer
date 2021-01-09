from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_lowercase(value: str):
    if value.lower() != value:
        raise ValidationError(_("Ensure the value is lower-cased."), code="invalid")


def validate_email_domain(value: str):
    user_part, domain_part = value.rsplit("@")
    validate_allowed_domain(domain_part)


def validate_allowed_domain(value: str):
    if not settings.LIMIT_DOMAINS_TO:
        return
    if value not in settings.LIMIT_DOMAINS_TO:
        raise ValidationError(
            _("You're not allowed to manage e-mail addresses for this domain."),
            code="domain-not-whitelisted",
        )

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_lowercase(value: str):
    if value.lower() != value:
        raise ValidationError(_("Ensure the value is lower-cased."), code="invalid")

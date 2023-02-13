from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from cryptography.hazmat.primitives import serialization


def validate_private_key(key: str):
    try:
        serialization.load_pem_private_key(key.encode(), password=None)
    except ValueError as exc:
        raise ValidationError(
            _("Provided key could not be loaded as private key")
        ) from exc

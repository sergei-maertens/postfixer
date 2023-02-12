from django.db import models
from django.utils.translation import gettext_lazy as _


class SigningAlgorithms(models.TextChoices):
    """
    Check with supported algorithms of OpenDKIM.

    Example:

        opendkim -V

        Supported signing algorithms:
            rsa-sha1
            rsa-sha256
            ed25519-sha256
    """

    rsa_sha1 = "rsa-sha1", _("rsa-sha1")
    rsa_sha256 = "rsa-sha256", _("rsa-sha256")
    # ed25519_sha256 = "ed25519-sha256", _("ed25519-sha256")
    # -> requires special treatment for DNS pubkey


class DKIMKey(models.Model):
    """
    Support signing keys for an entire domain.
    """

    domain_name = models.CharField(
        _("domain name"),
        max_length=255,
        help_text=_(
            "The (sub) domain, e.g. for user@example.com, enter 'example.com'."
        ),
    )
    selector = models.CharField(
        _("key selector"),
        max_length=63,
        help_text=_("Key selector, these typically change during key rotation."),
    )
    signing_algorithm = models.CharField(
        _("signing algorithm"),
        max_length=20,
        choices=SigningAlgorithms.choices,
        default=SigningAlgorithms.rsa_sha256,
    )
    private_key = models.TextField(
        _("private key"),
        help_text=_("Private key, in PEM format."),
    )
    public_key = models.TextField(
        _("public key"),
        help_text=_("Public key - this needs to be published in the DNS record."),
    )
    comments = models.TextField(_("comments"), blank=True)

    class Meta:
        verbose_name = _("DKIM keypair")
        verbose_name_plural = _("DKIM keypairs")

    def __str__(self):
        return self.dns_label

    @property
    def dns_label(self) -> str:
        return f"{self.selector}._domainkey.{self.domain_name}"

    @property
    def dns_public_key(self) -> str:
        assert self.signing_algorithm.startswith("rsa-")
        pubkey = (
            self.public_key.replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\r\n", "")
            .replace("\n", "")
        )
        return pubkey

    @property
    def txt_record(self) -> str:
        key_type, hash_algo = self.signing_algorithm.split("-")
        bits = [
            "v=DKIM1",
            f"h={hash_algo}",
            f"k={key_type}",
            f"p={self.dns_public_key}",
        ]
        return f'"{"; ".join(bits)}"'

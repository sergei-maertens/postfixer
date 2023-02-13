from django import forms
from django.utils.translation import gettext_lazy as _

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .models import DKIMKey


class DKIMKeyForm(forms.ModelForm):
    generate_keypair = forms.BooleanField(
        label=_("Generate keypair?"),
        required=False,
        initial=True,
        help_text=_("Check to generate a private/public key pair."),
    )

    class Meta:
        model = DKIMKey
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["private_key"].required = False
        self.fields["public_key"].required = False

        if self.instance and self.instance.private_key:
            self.fields["generate_keypair"].initial = False

    def clean(self):
        super().clean()

        generate_keypair = self.cleaned_data.get("generate_keypair")
        if not generate_keypair:
            privkey = self.cleaned_data.get("private_key", "")
            if not privkey:
                self.add_error(
                    "private_key",
                    _("You must either generate a key pair or provide a private key"),
                )

            pubkey = self.cleaned_data.get("public_key", "")
            if not pubkey:
                self.add_error(
                    "public_key",
                    _("You must either generate a key pair or provide a public key"),
                )

        return self.cleaned_data

    def save(self, *args, **kwargs):
        if self.cleaned_data["generate_keypair"]:
            privkey, pubkey = generate_rsa_keypair()
            self.instance.private_key = privkey
            self.instance.public_key = pubkey
        return super().save(*args, **kwargs)


def generate_rsa_keypair(key_size=2048) -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    privkey_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    pubkey_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return privkey_pem.decode(), pubkey_pem.decode()

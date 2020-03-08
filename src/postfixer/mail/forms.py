from django import forms
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as _AdminPasswordChangeForm
)
from django.utils.translation import ugettext_lazy as _

from .models import VirtualMailbox
from .password_schemes import (
    DEFAULT as DEFAULT_SCHEME, SCHEMES, hash_password, identify_hasher
)


class AdminPasswordChangeForm(_AdminPasswordChangeForm):
    hash_scheme = forms.ChoiceField(
        label=_("Hashing scheme"),
        help_text=_("Password hashing scheme to use"),
        choices=[(scheme, scheme) for scheme in SCHEMES],
    )

    def __init__(self, mailbox: VirtualMailbox, *args, **kwargs):
        self.mailbox = mailbox
        super(_AdminPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields["password1"].help_text = ""

        # have a sticky algorithm
        algo, _ = identify_hasher(self.mailbox.password)
        scheme = {v: k for k, v in SCHEMES.items()}[algo]
        self.fields["hash_scheme"].initial = scheme

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages["password_mismatch"], code="password_mismatch",
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.mailbox.password = hash_password(
            password, scheme=self.cleaned_data["hash_scheme"],
        )
        if commit:
            self.mailbox.save()
        return self.mailbox


class VirtualMailboxAddForm(forms.ModelForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
    }
    email = forms.EmailField(label=_("E-mail address"))
    password1 = forms.CharField(
        label=_("Password"), strip=False, widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    hash_scheme = forms.ChoiceField(
        label=_("Hashing scheme"),
        help_text=_("Password hashing scheme to use"),
        choices=[(scheme, scheme) for scheme in SCHEMES],
        initial=DEFAULT_SCHEME,
    )

    class Meta:
        model = VirtualMailbox
        fields = ("email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"], code="password_mismatch",
            )
        return password2

    def save(self, commit=True):
        mailbox = super().save(commit=False)
        mailbox.set_email(self.cleaned_data["email"])
        mailbox.password = hash_password(
            self.cleaned_data["password1"], scheme=self.cleaned_data["hash_scheme"],
        )
        if commit:
            mailbox.save()
        return mailbox


class VirtualMailboxChangeForm(forms.ModelForm):
    class Meta:
        model = VirtualMailbox
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].help_text = (
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            '<a href="../password/">this form</a>.'
        )
        self.fields["password"].disabled = True

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")

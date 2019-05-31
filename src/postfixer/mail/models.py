from django.db import models
from django.utils.translation import ugettext_lazy as _


class Domain(models.Model):
    name = models.CharField(_("domain name"), max_length=253, unique=True)
    comments = models.TextField(_("comments"), blank=True)

    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")

    def __str__(self):
        return self.name


class Forward(models.Model):
    source = models.CharField(_("source"), max_length=320, unique=True)
    destination = models.CharField(_("destination"), max_length=320)
    comments = models.TextField(_("comments"), blank=True)

    class Meta:
        verbose_name = _("forward")
        verbose_name_plural = _("forwards")

    def __str__(self):
        return f"{self.source} -> {self.destination}"

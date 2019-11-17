from django.contrib import admin

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import EmailPartsMixin as EmailPartsModelMixin, Forward, VirtualMailbox


class EmailPartsMixin:
    def get_queryset(self, request=None):
        return super().get_queryset(request=request).annotate_email()

    def email(self, obj: EmailPartsModelMixin) -> str:
        return obj.email


@admin.register(Forward)
class ForwardAdmin(EmailPartsMixin, DynamicArrayMixin, admin.ModelAdmin):
    list_display = ("email", "destinations", "comments", "active")
    list_filter = ("active", "domain_part")
    ordering = ("domain_part", "user_part")


@admin.register(VirtualMailbox)
class VirtualMailboxAdmin(EmailPartsMixin, admin.ModelAdmin):
    list_display = ("email", "active")
    list_filter = ("active", "domain_part")

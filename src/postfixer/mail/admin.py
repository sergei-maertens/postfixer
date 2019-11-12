from django.contrib import admin

from .models import Domain, Forward, VirtualMailbox


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "comments", "active")
    list_filter = ("active",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Forward)
class ForwardAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "comments", "active")
    list_filter = ("active",)
    search_fields = ("source", "destination")
    ordering = ("source",)


@admin.register(VirtualMailbox)
class VirtualMailboxAdmin(admin.ModelAdmin):
    list_display = ("email", "active")
    list_filter = ("active", "domain_part")

    def get_queryset(self, request=None):
        return super().get_queryset(request=request).annotate_email()

    def email(self, obj: VirtualMailbox) -> str:
        return obj.email

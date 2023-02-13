from django.contrib import admin

from .forms import DKIMKeyForm
from .models import DKIMKey


@admin.register(DKIMKey)
class DKIMKeyAdmin(admin.ModelAdmin):
    list_display = ("dns_label", "selector", "domain_name", "signing_algorithm")
    list_filter = ("domain_name", "signing_algorithm")
    search_fields = ("selector", "domain_name")
    readonly_fields = ("txt_record",)
    form = DKIMKeyForm

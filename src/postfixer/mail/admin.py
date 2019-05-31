from django.contrib import admin

from .models import Domain, Forward


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "comments")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Forward)
class ForwardAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "comments")
    search_fields = ("source", "destination")
    ordering = ("source",)

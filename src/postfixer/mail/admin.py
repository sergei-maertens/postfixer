from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import escape
from django.utils.translation import gettext, ugettext_lazy as _

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .forms import (
    AdminPasswordChangeForm,
    VirtualMailboxAddForm,
    VirtualMailboxChangeForm,
)
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

    form = VirtualMailboxChangeForm
    add_form = VirtualMailboxAddForm
    change_password_form = AdminPasswordChangeForm
    change_mailbox_password_template = "admin/mailbox/change_password.html"

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            path(
                "<id>/password/",
                self.admin_site.admin_view(self.mailbox_change_password),
                name="mail_virtualmailbox_password_change",
            ),
        ] + super().get_urls()

    @sensitive_post_parameters_m
    def mailbox_change_password(self, request, id, form_url=""):
        mailbox = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, mailbox):
            raise PermissionDenied
        if mailbox is None:
            raise Http404(
                _("%(name)s object with primary key %(key)r does not exist.")
                % {"name": self.model._meta.verbose_name, "key": escape(id),}
            )
        if request.method == "POST":
            form = self.change_password_form(mailbox, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, mailbox, change_message)
                msg = gettext("Password changed successfully.")
                messages.success(request, msg)
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_change"
                        % (
                            self.admin_site.name,
                            mailbox._meta.app_label,
                            mailbox._meta.model_name,
                        ),
                        args=(mailbox.pk,),
                    )
                )
        else:
            form = self.change_password_form(mailbox)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change password: %s") % escape(mailbox.get_email()),
            "adminForm": adminForm,
            "form_url": form_url,
            "form": form,
            "is_popup": (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": mailbox,
            "save_as": False,
            "show_save": True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_mailbox_password_template
            or "admin/auth/user/change_password.html",
            context,
        )

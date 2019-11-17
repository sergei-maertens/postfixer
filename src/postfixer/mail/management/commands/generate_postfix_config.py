from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import get_template

from ...models import Forward, VirtualMailbox


class Command(BaseCommand):
    help = "Generate the postfix-pgsql config bits"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--db-alias",
            default="default",
            help="Database alias to use credentials from, in case of multi-db setup. Defaults to 'default'",
        )
        parser.add_argument(
            "--template-name",
            default="mail/postfix.cf",
            help="Template file to use for the config",
        )

    def handle(self, **options) -> None:
        using = options["db_alias"]
        template = get_template(options["template_name"])
        db = settings.DATABASES[using]

        # when using virtual alias domains and virtual mailbox domains at the same
        # time, it's sufficient to list the alias & mailbox domains in virtual mailbox domains
        # in fact, postfix complains about having the domain in both

        # virtual aliases
        virtual_alias_qs = (
            Forward.objects.using(using)
            .filter(source="'%s'", active=True)
            .values("destination")
        )
        context = {
            "db": db,
            "setting": "virtual_alias_maps",
            "query": str(virtual_alias_qs.query),
        }
        result = template.render(context)
        self.stdout.write(result)

        # virtual mailbox domains
        virtual_mailbox_qs = VirtualMailbox.objects.using(using).get_domain("'%s'")
        context = {
            "db": db,
            "setting": "virtual_mailbox_domains",
            "query": str(virtual_mailbox_qs.query),
        }
        result = template.render(context)
        self.stdout.write(result)

        # virtual mailbox maps
        virtual_mailbox_maps_qs = VirtualMailbox.objects.using(using).get_maildir(
            "'%s'"
        )
        context = {
            "db": db,
            "setting": "virtual_mailbox_maps",
            "query": str(virtual_mailbox_maps_qs.query),
        }
        result = template.render(context)
        self.stdout.write(result)

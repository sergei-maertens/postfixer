from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import get_template

from ...models import Domain, Forward


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

        # virtual domains
        virtual_domains_qs = (
            Domain.objects.using(using).filter(name="'%s'", active=True).values("id")
        )
        context = {
            "db": db,
            "setting": "virtual_alias_domains",
            "query": str(virtual_domains_qs.query),
        }
        result = template.render(context)
        self.stdout.write(result)

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

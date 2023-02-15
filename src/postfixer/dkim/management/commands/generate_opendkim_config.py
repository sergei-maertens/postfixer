from dataclasses import dataclass
from textwrap import dedent
from typing import TypeVar, cast

from django.conf import settings
from django.core.management import BaseCommand
from django.db import models

from ...models import DKIMKey

ModelField = TypeVar("ModelField", bound=models.Field)


@dataclass
class ConnParams:
    keycol: str
    datacol: list[str]

    def as_opendkim_config(self) -> str:
        bits = [
            f"?keycol={self.keycol}",
            f"?datacol={','.join(self.datacol)}",
        ]
        return "".join(bits)


def get_column(field_name: str) -> str:
    model_field = cast(ModelField, DKIMKey._meta.get_field(field_name))
    return model_field.column


class Command(BaseCommand):
    help = "Generate the OpenDKIM config bits"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--db-alias",
            default="default",
            help="Database alias to use credentials from, in case of multi-db setup. Defaults to 'default'",
        )

    def handle(self, **options):
        using = options["db_alias"]
        db = settings.DATABASES[using]
        credentials = f"{db['USER']}:{db['PASSWORD']}@"
        conn_string = f"psql://{credentials}{db['PORT']}+{db['HOST']}/{db['NAME']}"
        dsn_base = f"dsn:{conn_string}/table={DKIMKey._meta.db_table}"
        signing_table_params = ConnParams(
            keycol=get_column("domain_name"),
            datacol=[get_column("id")],
        )
        keys_table_params = ConnParams(
            keycol=get_column("id"),
            datacol=[
                get_column("domain_name"),
                get_column("selector"),
                get_column("private_key"),
            ],
        )

        config = dedent(
            f"""
            SigningTable\t\t{dsn_base}{signing_table_params.as_opendkim_config()}
            KeysTable\t\t{dsn_base}{keys_table_params.as_opendkim_config()}
            """
        )
        self.stdout.write(config)

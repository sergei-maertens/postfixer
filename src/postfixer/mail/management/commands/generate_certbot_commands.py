import asyncio
from typing import List

from django.core.management import BaseCommand

from dns.asyncresolver import resolve

from ...models import Forward, VirtualMailbox

CMD = "{certbot} certonly --{plugin} -d SERVER_NAME {extra}"


async def get_mx_records(domains: List[str]) -> List[str]:
    tasks = [resolve(domain, "MX") for domain in domains]
    results = await asyncio.gather(*tasks)

    dns_names = {
        rdata.exchange.to_text(omit_final_dot=True)
        for result in results
        for rdata in result.rrset
    }

    return sorted(dns_names)


class Command(BaseCommand):
    help = "Generate the certbot cert generation command"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--db-alias",
            default="default",
            help="Database alias to use credentials from, in case of multi-db setup. Defaults to 'default'",
        )
        parser.add_argument("--certbot", default="/opt/certbot/certbot-auto")
        parser.add_argument("--plugin", default="nginx")

    def handle(self, **options) -> None:
        using = options["db_alias"]

        # all domains
        qs = (
            (
                Forward.objects.using(using)
                .values_list("domain_part", flat=True)
                .union(
                    VirtualMailbox.objects.using(using).values_list(
                        "domain_part", flat=True
                    )
                )
            )
            .order_by("domain_part")
            .distinct()
        )

        domains = list(qs)

        mx_domains = asyncio.run(get_mx_records(domains))

        extra = " ".join([f"-d {domain}" for domain in mx_domains])

        cmd = CMD.format(
            certbot=options["certbot"], plugin=options["plugin"], extra=extra,
        )

        self.stdout.write(cmd)

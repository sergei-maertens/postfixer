import subprocess
from typing import List

from django.conf import settings


def generate_cert(domains: List[str]) -> None:
    plugin = settings.CERTBOT_PLUGIN
    binary = settings.CERTBOT_BINARY

    args = [
        binary,
        f"--{plugin}",
    ]
    for domain in domains:
        args += ["-d", domain]

    subprocess.run(args)

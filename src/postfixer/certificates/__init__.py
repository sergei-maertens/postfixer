from typing import List

from .letsencrypt import generate_cert
from .utils import get_certificate_domains


def ensure_certificate_up_to_date(certificate_file: str, domains: List[str]) -> None:
    needs_generate, domains = get_certificate_domains(certificate_file, domains)

    if needs_generate:
        generate_cert(domains)

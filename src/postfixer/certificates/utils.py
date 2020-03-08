from typing import List, Tuple

import dns.resolver
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def extract_domains(certificate_file: str) -> List[str]:
    with open(certificate_file, "rb") as cert:
        cert = x509.load_pem_x509_certificate(cert.read(), default_backend())

    ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    subj_alt_names = ext.value.get_values_for_type(x509.DNSName)
    return subj_alt_names


def get_relevant_mx_hosts(domain: str) -> List[Tuple[str, List[str]]]:
    answers = dns.resolver.query(domain, "MX")

    mx_servers = [answer.exchange.to_text() for answer in answers]

    resolved = []
    for server in mx_servers:
        ips = [answer.to_text() for answer in dns.resolver.query(server, "A")]
        resolved.append((server, ips))

    return resolved

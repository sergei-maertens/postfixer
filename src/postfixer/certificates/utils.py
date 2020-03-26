from typing import List, Tuple

import dns.resolver
import dns.reversename
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
        resolved.append((server[:-1], ips))

    return resolved


def get_ptr(ip: str) -> str:
    addr = dns.reversename.from_address(ip)
    answer = dns.resolver.query(addr, "PTR")
    assert len(answer) == 1, "Received multipe PTR records"
    return answer[0].to_text()[:-1]


def get_certificate_domains(
    certificate_file: str, all_domains: List[str]
) -> Tuple[bool, List[str]]:
    """
    Determine which hosts are missing from the certificate.

    :param certificate_file: Path to the file containing the SSL certificate, in PEM format.
    :param all_domains: List of all relevant mail-handling domains. MX lookups will be
      performed to figure out the mail hosts.
    :return: Tuple (domains_missing, list_of_hosts) - a tuple indicating if any of the
      list_of_hosts are missing in the certificate, thus requiring a new cert to be
      generated.
    """
    hosts = extract_domains(certificate_file)

    # first domain in cert is considered to be the mail host name (which needs FQDN and
    # proper ptr record)
    mail_host = hosts[0]
    ips = [answer.to_text() for answer in dns.resolver.query(mail_host, "A")]
    ptrs = [get_ptr(ip) for ip in ips]

    # if multiple IP adresses are used for the mail host, we need to figure out the one
    # that's relevant -> check the PTR config, as mail servers with mis-matching PTR
    # do not practically work
    mail_ip = ips[ptrs.index(mail_host)]

    # we now have mail_ip that we can compare relevants hosts for
    mail_hosts = []
    for domain in all_domains:
        mx_hosts = get_relevant_mx_hosts(domain)
        for host, ips in mx_hosts:
            if mail_ip in ips:
                mail_hosts.append(host)
                break

    needs_update = not set(mail_hosts).issubset(set(hosts))

    # determine set of hosts required in cert. don't touch hosts that are in the cert
    # but not in all_domains (could be some external thing that manages it)
    all_hosts = set(hosts).union(set(mail_hosts))

    # finally - sort them into a list. maintain the order as they appear in the cert
    def _sort_key(host: str) -> Tuple[int, str]:
        try:
            index = hosts.index(host)
        except ValueError:
            index = 1000
        return (index, host)

    final_hosts = sorted(all_hosts, key=_sort_key)
    return (needs_update, final_hosts)

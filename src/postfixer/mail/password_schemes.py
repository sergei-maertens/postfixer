"""
Implement the password hashing for virtual mailboxes.

See https://doc.dovecot.org/configuration_manual/authentication/password_schemes/#what-scheme-to-use
for a reference of available schemes.

Ubuntu 18.04 dovecot does not support:
- ARGON2I/ARGON2ID
- BLF-CRYPT

Next best thing is SHA512-CRYPT
"""
from typing import Tuple

from passlib.hash import md5_crypt, plaintext, sha256_crypt, sha512_crypt
from passlib.utils.handlers import GenericHandler

DEFAULT = "SHA512-CRYPT"

SCHEMES = {
    "SHA512-CRYPT": sha512_crypt,
    "SHA256-CRYPT": sha256_crypt,
    "MD5-CRYPT": md5_crypt,
    "PLAIN": plaintext,
}

assert DEFAULT in SCHEMES


def hash_password(password: str, scheme: str = DEFAULT) -> str:
    try:
        algorithm = SCHEMES[scheme]
    except KeyError:
        raise KeyError(f"The scheme {scheme} is not supported")

    hashed = algorithm.hash(password)
    return f"{{{scheme}}}{hashed}"


def identify_hasher(hashed: str) -> Tuple[GenericHandler, str]:
    # no explicit algorithm -> use the default
    if not hashed.startswith("{"):
        return SCHEMES[DEFAULT], hashed

    if "}" not in hashed:
        raise ValueError(f"Can't determine scheme for hash {hashed}")

    # get the scheme between {SCHEME}restofhash

    scheme, actual_hash = hashed[1:].split("}", 1)
    if scheme not in SCHEMES:
        supported_schemes = ", ".join(SCHEMES.keys())
        raise ValueError(
            f"Scheme {scheme} is not supported (must be one of {supported_schemes})"
        )

    algorithm = SCHEMES[scheme]
    return (algorithm, actual_hash)


def check_password(password: str, hashed: str) -> bool:
    algorithm, actual_hash = identify_hasher(hashed)
    return algorithm.verify(password, actual_hash)

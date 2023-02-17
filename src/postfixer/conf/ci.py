"""
Continuous integration settings module.
"""
import os
import warnings

os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("SECRET_KEY", "dummy")

from .base import *  # noqa isort:skip

# shut up logging
LOGGING["loggers"].update(
    {
        "openforms.api.exception_handling": {
            "handlers": ["console"],
            "level": "CRITICAL",
            "propagate": False,
        },
    }
)

# don't spend time on password hashing in tests/user factories
PASSWORD_HASHERS = ["django.contrib.auth.hashers.UnsaltedMD5PasswordHasher"]

ENVIRONMENT = "CI"

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)

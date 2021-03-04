"""(deprecated) Module that defines various constants for interacting with the Vivint Sky API.

This module has been deprecated in favor of `const`.
"""


from .const import *
from .utils import send_deprecation_warning


def __getattr__(name):
    """Log a warning."""
    send_deprecation_warning("pyvivint.constants", "pyvivint.const")
    return name

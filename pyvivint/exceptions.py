"""The exceptions used by the pyvivint library."""


class VivintError(Exception):
    """General pyvivint exception occurred."""


class VivintSkyApiError(VivintError):
    """VivintSky API related exception occurred."""


class VivintSkyApiAuthenticationError(VivintSkyApiError):
    """VivintSky API authentication related error occurred."""


class VivintSkyApiExpiredTokenError(VivintSkyApiError):
    """VivintSky API token expired error occurred."""


class VivintSkyApiMissingTokenError(VivintSkyApiError):
    """VivintSky API missing id token error occurred."""

"""The exceptions used by the vivintpy library."""


class VivintError(Exception):
    """General vivintpy exception occurred."""


class VivintSkyApiError(VivintError):
    """VivintSky API related exception occurred."""


class VivintSkyApiAuthenticationError(VivintSkyApiError):
    """VivintSky API authentication related error occurred."""


class VivintSkyApiMfaRequiredError(VivintSkyApiAuthenticationError):
    """VivintSky API MFA required related error occurred."""


class VivintSkyApiExpiredCookieError(VivintSkyApiError):
    """VivintSky API cookie expired error occurred."""


class VivintSkyApiMissingCookieError(VivintSkyApiError):
    """VivintSky API missing cookie error occurred."""

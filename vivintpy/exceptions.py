"""The exceptions used by the vivintpy library."""

from __future__ import annotations

import grpc


class VivintError(Exception):
    """General vivintpy exception occurred."""


class VivintSkyApiError(VivintError):
    """VivintSky API related exception occurred."""


class VivintSkyApiRateLimitError(VivintSkyApiError):
    """VivintSky API rate limit exceeded error occurred.

    Thermostat changes are limited to a few per minute per command.
    """


class VivintSkyApiAuthenticationError(VivintSkyApiError):
    """VivintSky API authentication related error occurred."""


class VivintSkyClimateAuthenticationError(VivintSkyApiAuthenticationError):
    """The climate service rejected the credentials while loading thermostats.

    Thermostats are optional, so a refresh of several systems carries on and raises
    this once it is done.
    """


class VivintSkyApiMfaRequiredError(VivintSkyApiAuthenticationError):
    """VivintSky API MFA required related error occurred."""


class VivintSkyApiExpiredCookieError(VivintSkyApiError):
    """VivintSky API cookie expired error occurred."""


class VivintSkyApiMissingCookieError(VivintSkyApiError):
    """VivintSky API missing cookie error occurred."""


class VivintSkyGrpcError(VivintSkyApiError):
    """A VivintSky gRPC service rejected a request."""

    def __init__(self, method: str, code: grpc.StatusCode, details: str | None) -> None:
        """Initialize the error with the rejected method and its status."""
        super().__init__(f"{method} failed: {code.name}: {details or 'no details'}")
        self.method = method
        self.code = code


class SpaceMonkeyError(VivintError):
    """Space Monkey DVR related exception occurred."""

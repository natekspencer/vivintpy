from warnings import warn

from .account import Account, Optional, aiohttp


class Vivint(Account):
    """Vivint class (for backwards compatibility.

    This class has been deprecated in favor of `Account`.
    """

    def __init__(
        self,
        username: str,
        password: str,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        warn(
            f"Vivint has been deprecated in favor of Account, the alias will be removed in the future",
            DeprecationWarning,
            stacklevel=2,
        )
        return super().__init__(username, password, client_session)

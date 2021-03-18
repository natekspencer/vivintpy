from .account import Account, Optional, aiohttp
from .utils import send_deprecation_warning


class Vivint(Account):
    """(deprecated) Vivint class.

    This class has been deprecated in favor of `Account`.
    """

    def __init__(
        self,
        username: str,
        password: str,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        send_deprecation_warning("vivintpy.vivint.Vivint", "vivintpy.account.Account")
        return super().__init__(username, password, client_session)

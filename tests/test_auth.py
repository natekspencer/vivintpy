"""Test logging in with a refresh token."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from aiohttp import ClientConnectionError

from vivintpy.account import Account
from vivintpy.api import VivintSkyApi
from vivintpy.exceptions import VivintSkyApiAuthenticationError, VivintSkyApiError

USERNAME = "user@example.com"


def token_response(refresh_token: str | None, expired: bool = False) -> dict[str, Any]:
    """Return a token response."""
    delta = timedelta(hours=-1 if expired else 1)
    response = {
        "access_token": "access",
        "id_token": jwt.encode(
            {"exp": datetime.now(UTC) + delta}, "a-test-secret-of-sufficient-length"
        ),
    }
    if refresh_token:
        response["refresh_token"] = refresh_token
    return response


def create_api(post: AsyncMock, **kwargs: Any) -> Any:
    """Return an API using a custom session and the given token endpoint."""
    api: Any = VivintSkyApi(username=USERNAME, client_session=MagicMock(), **kwargs)
    api._VivintSkyApi__post = post
    api._VivintSkyApi__get = AsyncMock(return_value={"other": True})
    api.get_authuser_data = AsyncMock(return_value={"u": {}})
    return api


def posted_tokens(post: AsyncMock) -> list[str]:
    """Return the refresh tokens that were sent."""
    return [call.kwargs["data"]["refresh_token"] for call in post.call_args_list]


async def test_connect_without_a_password() -> None:
    """Test a refresh token is enough to connect."""
    post = AsyncMock(return_value=token_response("second"))
    api = create_api(post, refresh_token="first")

    assert await api.connect() == {"u": {}}

    assert posted_tokens(post) == ["first"]
    assert api.tokens["refresh_token"] == "second"


async def test_reconnect_uses_the_latest_refresh_token() -> None:
    """Test a session that expires is renewed with the newest token."""
    post = AsyncMock(
        side_effect=[token_response("second", True), token_response("third")]
    )
    api = create_api(post, refresh_token="first")

    with pytest.raises(VivintSkyApiAuthenticationError):
        await api.connect()
    await api.connect()

    assert posted_tokens(post) == ["first", "second"]


async def test_refresh_response_without_a_new_token_keeps_the_old_one() -> None:
    """Test a token that doesn't rotate isn't lost."""
    post = AsyncMock(return_value=token_response(None))
    api = create_api(post, refresh_token="first")

    await api.connect()

    assert api.tokens["refresh_token"] == "first"


async def test_concurrent_connects_refresh_once() -> None:
    """Test requests that find an expired session don't reuse the refresh token."""

    async def refresh(**_: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        return token_response("second")

    post = AsyncMock(side_effect=refresh)
    api = create_api(post, refresh_token="first")

    await asyncio.gather(api.connect(), api.connect(), api.connect())

    assert posted_tokens(post) == ["first"]


async def test_refresh_token_changed_callback() -> None:
    """Test the callback gets each new token, and only when it changes."""
    callback = MagicMock()
    post = AsyncMock(
        side_effect=[
            token_response("second", True),
            token_response("second", True),
            token_response("third"),
        ]
    )
    api = create_api(post, refresh_token="first", on_refresh_token_changed=callback)

    for _ in range(2):
        with pytest.raises(VivintSkyApiAuthenticationError):
            await api.connect()
    await api.connect()

    assert [call.args[0] for call in callback.call_args_list] == ["second", "third"]


async def test_connect_without_credentials() -> None:
    """Test there is a clear error when there is nothing to log in with."""
    post = AsyncMock()
    api = create_api(post)

    with pytest.raises(VivintSkyApiAuthenticationError, match="password"):
        await api.connect()

    post.assert_not_called()


async def test_expired_refresh_without_a_password() -> None:
    """Test a refresh that doesn't give a valid session asks for a password."""
    post = AsyncMock(return_value=token_response("second", True))
    api = create_api(post, refresh_token="first")

    with pytest.raises(VivintSkyApiAuthenticationError, match="password"):
        await api.connect()


def create_account(error: Exception) -> Account:
    """Return an account whose request for user data fails."""
    with patch("vivintpy.account.VivintSkyApi") as api_cls:
        account = Account(username=USERNAME, refresh_token="first")
    api_cls.return_value.get_authuser_data = AsyncMock(side_effect=error)
    return account


async def test_account_refresh_raises_authentication_errors() -> None:
    """Test callers find out when the account needs logging in again."""
    account = create_account(VivintSkyApiAuthenticationError("invalid_grant"))

    with pytest.raises(VivintSkyApiAuthenticationError):
        await account.refresh()


@pytest.mark.parametrize(
    "error", [VivintSkyApiError("Unavailable"), ClientConnectionError()]
)
async def test_account_refresh_logs_connection_errors(error: Exception) -> None:
    """Test a temporary failure doesn't raise."""
    await create_account(error).refresh()

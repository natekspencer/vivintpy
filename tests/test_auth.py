"""Test logging in with a refresh token."""

from __future__ import annotations

import asyncio
import json
import warnings
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from aiohttp import ClientConnectionError

from vivintpy.account import Account
from vivintpy.api import VivintSkyApi
from vivintpy.exceptions import (
    VivintSkyApiAuthenticationError,
    VivintSkyApiError,
    VivintSkyApiMfaRequiredError,
)

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


async def test_refresh_token_changed_callback_for_a_supplied_token() -> None:
    """Test a different token is reported even if the response has no new one."""
    callback = MagicMock()
    post = AsyncMock(return_value=token_response(None))
    api = create_api(post, refresh_token="first", on_refresh_token_changed=callback)

    await api.refresh_token("other")

    callback.assert_called_once_with("other")
    assert api.tokens["refresh_token"] == "other"


async def test_connect_with_a_valid_session_does_not_refresh() -> None:
    """Test the default session isn't renewed while it is still valid."""
    post = AsyncMock(return_value=token_response("second"))
    api: Any = VivintSkyApi(username=USERNAME, refresh_token="first")
    api._VivintSkyApi__post = post
    api.get_authuser_data = AsyncMock(return_value={"u": {}})

    await api.connect()
    await api.connect()
    await api.disconnect()

    assert posted_tokens(post) == ["first"]


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
async def test_account_refresh_logs_connection_errors(
    error: Exception, caplog: pytest.LogCaptureFixture
) -> None:
    """Test a temporary failure is logged and doesn't raise."""
    await create_account(error).refresh()

    assert "Unable to refresh system(s)" in caplog.text


def stored_passwords(api: Any) -> list[str | None]:
    """Return the passwords an API is holding on to."""
    return [api._VivintSkyApi__password, api._VivintSkyApi__mfa_password]


def posted_passwords(post: AsyncMock) -> list[str]:
    """Return the passwords that were sent."""
    return [
        json.loads(call.kwargs["data"])["password"]
        for call in post.call_args_list
        if isinstance(call.kwargs["data"], str)
    ]


async def test_connect_with_a_password_does_not_keep_it() -> None:
    """Test a password passed to connect isn't stored."""
    post = AsyncMock(return_value=token_response("first"))
    api = create_api(post)

    await api.connect(password="secret")

    assert posted_passwords(post) == ["secret"]
    assert stored_passwords(api) == [None, None]


async def test_password_login_reports_the_refresh_token() -> None:
    """Test a login that returns tokens straight away calls the callback."""
    tokens: list[str] = []
    post = AsyncMock(return_value=token_response("first"))
    api = create_api(post, on_refresh_token_changed=tokens.append)

    await api.connect(password="secret")

    assert tokens == ["first"]


async def test_connect_password_replaces_a_rejected_refresh_token() -> None:
    """Test the password is used when the refresh token is rejected."""
    tokens: list[str] = []
    post = AsyncMock(
        side_effect=[
            VivintSkyApiAuthenticationError("invalid_grant"),
            token_response("second"),
        ]
    )
    api = create_api(
        post, refresh_token="first", on_refresh_token_changed=tokens.append
    )

    await api.connect(password="secret")

    assert posted_passwords(post) == ["secret"]
    assert tokens == ["second"]


async def test_rejected_refresh_token_needs_the_password_again() -> None:
    """Test a password from an earlier login can't be used later."""
    post = AsyncMock(return_value=token_response("first", True))
    api = create_api(post)
    await api.connect(password="secret")

    post.reset_mock(return_value=True)
    post.side_effect = VivintSkyApiAuthenticationError("invalid_grant")
    with pytest.raises(VivintSkyApiAuthenticationError, match="invalid_grant"):
        await api.connect()

    assert posted_passwords(post) == []


async def test_deprecated_password_is_still_used() -> None:
    """Test a password from the constructor works when the token is rejected."""
    post = AsyncMock(return_value=token_response("first", True))
    with pytest.warns(DeprecationWarning, match="2027.1.0"):
        api = create_api(post, password="secret")
    await api.connect()

    post.reset_mock(return_value=True)
    post.side_effect = [
        VivintSkyApiAuthenticationError("invalid_grant"),
        token_response("second"),
    ]
    await api.connect()

    assert posted_passwords(post) == ["secret"]
    assert api.tokens["refresh_token"] == "second"


def test_account_warns_once_about_a_deprecated_password() -> None:
    """Test the warning points at the caller, and isn't repeated by the API."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Account(username=USERNAME, password="secret", client_session=MagicMock())

    assert [warning.filename for warning in caught] == [__file__]
    assert caught[0].category is DeprecationWarning


def test_account_keeps_a_deprecated_password() -> None:
    """Test a password from the constructor still reaches the API."""
    with pytest.warns(DeprecationWarning):
        account = Account(
            username=USERNAME, password="secret", client_session=MagicMock()
        )

    assert stored_passwords(account.api)[0] == "secret"


def test_no_warning_without_a_password() -> None:
    """Test the constructor only warns when given a password."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        Account(username=USERNAME, client_session=MagicMock())


@pytest.mark.parametrize("challenge", ["response", "error"])
async def test_mfa_keeps_the_password_until_it_succeeds(challenge: str) -> None:
    """Test a wrong code can be retried, and the password is dropped afterwards."""
    required = VivintSkyApiMfaRequiredError("MFA required")
    post = AsyncMock(
        side_effect=[
            {"mfa": ""} if challenge == "response" else required,
            VivintSkyApiAuthenticationError("Invalid code"),
            {"url": "/next"},
            token_response("first"),
        ]
    )
    api = create_api(post)

    with pytest.raises(VivintSkyApiMfaRequiredError):
        await api.connect(password="secret")
    with pytest.raises(VivintSkyApiAuthenticationError, match="Invalid code"):
        await api.verify_mfa("000000")
    assert stored_passwords(api) == [None, "secret"]

    api._VivintSkyApi__get = AsyncMock(return_value={"location": "vivint://?code=abc"})
    await api.verify_mfa("123456")

    assert posted_passwords(post) == ["secret"] * 3
    assert stored_passwords(api) == [None, None]


async def test_disconnect_drops_a_password_waiting_for_mfa() -> None:
    """Test an abandoned MFA login doesn't keep the password."""
    api = create_api(AsyncMock(return_value={"mfa": ""}))

    with pytest.raises(VivintSkyApiMfaRequiredError):
        await api.connect(password="secret")
    await api.disconnect()

    assert stored_passwords(api) == [None, None]
    assert api._VivintSkyApi__mfa_pending is False


def create_mfa_account() -> tuple[Account, MagicMock]:
    """Return an account that needs MFA, and the API it uses."""
    with patch("vivintpy.account.VivintSkyApi") as api_cls:
        account = Account(username=USERNAME)
    api = api_cls.return_value
    api.connect = AsyncMock(side_effect=VivintSkyApiMfaRequiredError("MFA required"))
    api.verify_mfa = AsyncMock()
    api.disconnect = AsyncMock()
    api.get_authuser_data = AsyncMock(
        return_value={"u": {"_id": "user", "mbc": "channel", "system": []}}
    )
    return account, api


async def test_verify_mfa_finishes_connecting() -> None:
    """Test MFA subscribes when asked to, and disconnect then cleans up."""
    account, api = create_mfa_account()

    with patch("vivintpy.account.PubNubAsyncio") as pubnub_cls:
        pubnub = pubnub_cls.return_value
        pubnub.stop = AsyncMock()
        with pytest.raises(VivintSkyApiMfaRequiredError):
            await account.connect(subscribe_for_realtime_updates=True, password="s")
        await account.verify_mfa("123456")

        api.connect.assert_awaited_once_with("s")
        api.verify_mfa.assert_awaited_once_with("123456")
        assert account.connected
        pubnub_cls.assert_called_once()

        # callers that already subscribe after MFA shouldn't get a second connection
        await account.subscribe_for_realtime_updates()
        pubnub_cls.assert_called_once()

        await account.disconnect()

    pubnub.stop.assert_awaited_once()
    assert not account.connected


async def test_verify_mfa_only_subscribes_when_asked() -> None:
    """Test MFA doesn't subscribe if connect wasn't asked to."""
    account, _ = create_mfa_account()

    with patch("vivintpy.account.PubNubAsyncio") as pubnub_cls:
        with pytest.raises(VivintSkyApiMfaRequiredError):
            await account.connect(password="secret")
        await account.verify_mfa("123456")

    pubnub_cls.assert_not_called()


async def test_rejected_refresh_token_is_not_kept() -> None:
    """Test a login without a new token doesn't bring the rejected one back."""
    post = AsyncMock(
        side_effect=[
            VivintSkyApiAuthenticationError("invalid_grant"),
            token_response(None),
        ]
    )
    api = create_api(post, refresh_token="first")

    await api.connect(password="secret")

    assert api.tokens["refresh_token"] is None


async def test_mfa_during_a_refresh_keeps_the_password() -> None:
    """Test an MFA challenge to a refresh isn't treated as a rejected token."""
    post = AsyncMock(side_effect=VivintSkyApiMfaRequiredError("MFA required"))
    api = create_api(post, refresh_token="first")

    with pytest.raises(VivintSkyApiMfaRequiredError):
        await api.connect(password="secret")

    post.assert_awaited_once()
    assert stored_passwords(api) == [None, "secret"]


async def test_verify_mfa_finishes_an_incomplete_session() -> None:
    """Test MFA completes the login if it didn't return any tokens."""
    account, api = create_mfa_account()
    api.is_session_valid = MagicMock(return_value=False)
    api.connect = AsyncMock()

    await account.verify_mfa("123456")

    api.connect.assert_awaited_once_with()
    assert account.connected


async def test_verify_mfa_without_a_session_is_not_connected() -> None:
    """Test a login that can't be completed isn't reported as connected."""
    account, api = create_mfa_account()
    api.is_session_valid = MagicMock(return_value=False)
    api.connect = AsyncMock(side_effect=VivintSkyApiAuthenticationError("password"))

    with pytest.raises(VivintSkyApiAuthenticationError):
        await account.verify_mfa("123456")

    assert not account.connected


async def test_failed_subscribe_can_be_retried() -> None:
    """Test a subscribe that fails doesn't count as being subscribed."""
    account, _ = create_mfa_account()

    with patch("vivintpy.account.PubNubAsyncio") as pubnub_cls:
        pubnub_cls.return_value.subscribe.side_effect = [RuntimeError, MagicMock()]
        with pytest.raises(RuntimeError):
            await account.subscribe_for_realtime_updates()
        await account.subscribe_for_realtime_updates()

    assert pubnub_cls.call_count == 2


async def test_failed_authorization_retry_keeps_the_access_token() -> None:
    """Test the token is kept when signing in again for a code fails."""
    api = create_api(AsyncMock(), refresh_token="first")
    token = token_response("first")
    api._VivintSkyApi__token = token
    api._VivintSkyApi__get = AsyncMock(return_value={})
    api.connect = AsyncMock(side_effect=VivintSkyApiError("outage"))

    with pytest.raises(VivintSkyApiError):
        await api.get_authorization_code("client", "https://example.test/cb")

    assert api.tokens is token
    assert api.is_session_valid()


async def test_failed_authorization_retry_keeps_the_refresh_token() -> None:
    """Test the refresh token is restored when the password sign-in fails."""
    api = create_api(AsyncMock(), password="secret", refresh_token="first")
    api._VivintSkyApi__token = token_response("first")
    api._VivintSkyApi__get = AsyncMock(return_value={})
    api.connect = AsyncMock(side_effect=VivintSkyApiError("outage"))

    with pytest.raises(VivintSkyApiError):
        await api.get_authorization_code("client", "https://example.test/cb")

    assert api._VivintSkyApi__refresh_token == "first"


async def test_failed_authorization_retry_does_not_restore_a_consumed_token() -> None:
    """Test a refresh token that connect() consumed is not put back."""
    api = create_api(AsyncMock(), refresh_token="first")
    api._VivintSkyApi__token = token_response("first")
    api._VivintSkyApi__get = AsyncMock(return_value={})

    async def consume_refresh_token() -> None:
        api._VivintSkyApi__refresh_token = None
        raise VivintSkyApiError("rejected")

    api.connect = AsyncMock(side_effect=consume_refresh_token)

    with pytest.raises(VivintSkyApiError):
        await api.get_authorization_code("client", "https://example.test/cb")

    assert api._VivintSkyApi__refresh_token is None


async def test_failed_authorization_retry_clears_the_mfa_state() -> None:
    """Test MFA started by the forced sign-in doesn't block the restored tokens."""
    api = create_api(AsyncMock(), password="secret", refresh_token="first")
    token = token_response("first")
    api._VivintSkyApi__token = token
    api._VivintSkyApi__get = AsyncMock(return_value={})

    async def require_mfa() -> None:
        api._VivintSkyApi__mfa_pending = True
        api._VivintSkyApi__mfa_password = "secret"
        raise VivintSkyApiMfaRequiredError("MFA required")

    api.connect = AsyncMock(side_effect=require_mfa)

    with pytest.raises(VivintSkyApiMfaRequiredError):
        await api.get_authorization_code("client", "https://example.test/cb")

    assert api.tokens is token
    assert api._VivintSkyApi__mfa_pending is False
    assert api._VivintSkyApi__mfa_password is None

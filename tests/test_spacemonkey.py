"""Test the Space Monkey DVR client."""

from __future__ import annotations

import base64
import ssl
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any, Self
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from aiohttp import ClientSession, CookieJar, web
from aiohttp.test_utils import TestServer
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from vivintpy import spacemonkey
from vivintpy.account import Account
from vivintpy.exceptions import SpaceMonkeyError
from vivintpy.spacemonkey import (
    DvrRecording,
    SpaceMonkeyDvr,
    find_dvr_service_id,
    parse_playlist,
)
from vivintpy.system import System

HARDWARE_ID = "0123456789abcdef0123456789abcdef01234567"
START = datetime(2026, 10, 24, 18, 0, tzinfo=UTC)
PLAYLIST = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:14
#EXT-X-MEDIA-SEQUENCE:1
#EXTINF:13.5,
stream1.ts
#EXTINF:12.0,
stream2.ts
#EXTINF:12.0,
stream3.ts
#EXT-X-ENDLIST
"""


def _name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def _certificate(
    subject: str, issuer: str, key: Any, signer: Any, *, ca: bool
) -> x509.Certificate:
    now = datetime.now(UTC)
    return (
        x509.CertificateBuilder()
        .subject_name(_name(subject))
        .issuer_name(_name(issuer))
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(signer, hashes.SHA256())
    )


@pytest.fixture(name="bundle")
def bundle_fixture() -> bytes:
    """Return a PKCS#12 bundle shaped like the one Space Monkey issues."""
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root = _certificate("test-root", "test-root", root_key, root_key, ca=True)
    # The DVR issues 1024-bit client keys.
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    leaf = _certificate(f"{HARDWARE_ID}:0", "test-root", leaf_key, root_key, ca=False)
    return bytes(
        pkcs12.serialize_key_and_certificates(
            b"client", leaf_key, leaf, [root], serialization.NoEncryption()
        )
    )


class FakeApi:
    """Stand-in for VivintSkyApi that hands out a fixed authorization code."""

    async def get_authorization_code(self, *_args: Any, **_kwargs: Any) -> str:
        """Return an authorization code."""
        return "code123"


def test_find_dvr_service_id() -> None:
    """Test finding the DVR service in a system's data."""
    data = {
        "system": {
            "srvs": [
                {"t": "MYQ", "exid": "other"},
                {"t": "SPMO_DVR", "exid": "dvr-id"},
            ]
        }
    }
    assert find_dvr_service_id(data) == "dvr-id"
    assert find_dvr_service_id({"system": {"srvs": [{"t": "MYQ"}]}}) is None
    assert find_dvr_service_id({}) is None


def test_parse_playlist() -> None:
    """Test placing playlist segments on the recording's timeline."""
    recording = DvrRecording(
        "2026-10-24-18:00:00", 27, START, START + timedelta(hours=1)
    )
    segments = parse_playlist(PLAYLIST, recording)

    assert [s.number for s in segments] == [1, 2, 3]
    assert [s.start - START for s in segments] == [
        timedelta(seconds=0),
        timedelta(seconds=13.5),
        timedelta(seconds=25.5),
    ]
    assert segments[1].end == segments[2].start
    assert all(s.recording_id == recording.id for s in segments)


def test_ssl_context_requires_a_verified_server(bundle: bytes) -> None:
    """Test the TLS context presents the client certificate and verifies the server."""
    context = spacemonkey._build_ssl_context(bundle)  # pylint: disable=protected-access

    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname
    assert len(context.get_ca_certs()) == 1


def test_ssl_context_rejects_bundle_without_key() -> None:
    """Test a bundle that holds only certificates is refused."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    cert = _certificate("only-cert", "only-cert", key, key, ca=True)
    bundle = pkcs12.serialize_key_and_certificates(
        b"x", None, cert, None, serialization.NoEncryption()
    )
    with pytest.raises(SpaceMonkeyError):
        spacemonkey._build_ssl_context(bundle)  # pylint: disable=protected-access


@pytest_asyncio.fixture(name="cloud")
async def cloud_fixture(
    bundle: bytes, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[dict[str, Any]]:
    """Run a fake Space Monkey cloud and point the client at it."""
    calls: dict[str, Any] = {"paths": []}

    async def authorized(request: web.Request) -> web.Response:
        calls["paths"].append(request.path)
        calls["code"] = request.query.get("code")
        response = web.json_response({"response": {"message": "Success"}})
        response.set_cookie("session", "abc")
        return response

    async def certs(request: web.Request) -> web.Response:
        calls["paths"].append(request.path)
        calls["session"] = request.cookies.get("session")
        calls["dvr_service_id"] = request.query.get("dvr_service_id")
        expires = datetime.now(UTC) + timedelta(hours=24)
        return web.json_response(
            {
                "pkcs12_b64": base64.b64encode(bundle).decode(),
                "hw_id": HARDWARE_ID,
                "expires_at": expires.isoformat().replace("+00:00", "Z"),
            }
        )

    async def directory(request: web.Request) -> web.Response:
        calls["paths"].append(request.path)
        return web.json_response(
            {
                "address": {
                    "lan_dns": "ip4-192-168-1-167.example.test:8080",
                    "local_ip": "192.0.2.10",
                    "local_port": 8080,
                },
                "id": HARDWARE_ID,
            }
        )

    app = web.Application()
    app.router.add_get("/users/vivint/authorized", authorized)
    app.router.add_get("/v2/playback/certs", certs)
    app.router.add_get(f"/directory/mm/entry/hardware/{HARDWARE_ID}", directory)
    server = TestServer(app)
    await server.start_server()
    base = str(server.make_url("")).rstrip("/")
    monkeypatch.setattr(spacemonkey, "ACCOUNTS_ENDPOINT", base)
    monkeypatch.setattr(spacemonkey, "REDIRECT_URI", f"{base}/users/vivint/authorized")
    monkeypatch.setattr(spacemonkey, "DIRECTORY_ENDPOINT", base)
    yield calls
    await server.close()


@pytest.mark.asyncio
async def test_connect(cloud: dict[str, Any]) -> None:
    """Test signing in, getting a certificate and locating the DVR."""
    # The default cookie jar refuses cookies from the test server's IP address.
    async with ClientSession(cookie_jar=CookieJar(unsafe=True)) as session:
        dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
        connected_before = dvr.connected

        await dvr.connect()

        assert not connected_before
        assert dvr.connected
        assert cloud["code"] == "code123"
        assert cloud["session"] == "abc"
        assert cloud["dvr_service_id"] == "dvr-id"
        assert dvr.hardware_id == HARDWARE_ID
        assert dvr.address is not None
        assert dvr.address.host == "ip4-192-168-1-167.example.test"
        assert dvr.address.port == 8080
        assert dvr.address.local_ip == "192.0.2.10"
        assert dvr.certificate_expiry is not None
        assert dvr.certificate_expiry > datetime.now(UTC) + timedelta(hours=23)

        await dvr.disconnect()


@pytest.mark.asyncio
async def test_certificate_is_renewed_before_expiry(cloud: dict[str, Any]) -> None:
    """Test a certificate close to expiring is replaced before the next request."""
    async with ClientSession(cookie_jar=CookieJar(unsafe=True)) as session:
        dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
        await dvr.connect()
        dvr.certificate_expiry = datetime.now(UTC) + timedelta(minutes=5)
        cloud["paths"].clear()

        await dvr._ensure_connected()  # pylint: disable=protected-access

        assert "/v2/playback/certs" in cloud["paths"]
        assert dvr.certificate_expiry > datetime.now(UTC) + timedelta(hours=23)


@pytest.mark.asyncio
async def test_get_recordings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading the recorded ranges for a camera."""
    start, end = START, START + timedelta(hours=12)
    payload = {
        "Ranges": [
            {
                "Id": "2026-10-24-18:00:00",
                "CameraId": 27,
                "StartTime": int(start.timestamp() * 1_000_000),
                "EndTime": int(end.timestamp() * 1_000_000),
            }
        ]
    }
    requested: dict[str, Any] = {}

    class FakeResponse:
        """Minimal async context manager standing in for a ClientResponse."""

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def json(self) -> dict:
            return payload

    async def fake_get(_self: SpaceMonkeyDvr, path: str, **params: str) -> FakeResponse:
        requested.update(path=path, params=params)
        return FakeResponse()

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    recordings = await dvr.get_recordings(27)

    assert requested == {"path": "/recordings", "params": {"camera": "Video-27"}}
    assert recordings == [DvrRecording("2026-10-24-18:00:00", 27, start, end)]


@pytest.mark.asyncio
async def test_supplied_session_is_not_closed() -> None:
    """Test a session supplied by the caller stays open after disconnecting."""
    async with ClientSession() as session:
        dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
        await dvr.disconnect()
        assert not session.closed


def test_ssl_context_rejects_unreadable_bundle() -> None:
    """Test a bundle that is not a PKCS#12 file is reported as a DVR error."""
    with pytest.raises(SpaceMonkeyError, match="could not be read"):
        spacemonkey._build_ssl_context(b"not a bundle")  # pylint: disable=protected-access


def test_ssl_context_rejects_bundle_without_authorities() -> None:
    """Test a bundle without the CAs that sign the DVR's certificate is refused."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    cert = _certificate("leaf", "leaf", key, key, ca=False)
    bundle = pkcs12.serialize_key_and_certificates(
        b"x", key, cert, None, serialization.NoEncryption()
    )
    with pytest.raises(SpaceMonkeyError, match="authorities"):
        spacemonkey._build_ssl_context(bundle)  # pylint: disable=protected-access


class JsonResponse:
    """Minimal async context manager standing in for a ClientResponse."""

    def __init__(self, payload: Any) -> None:
        self._payload = payload

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    async def json(self) -> Any:
        return self._payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("payload", "expected"),
    [({"Ranges": None}, []), ({}, [])],
)
async def test_get_recordings_without_ranges(
    monkeypatch: pytest.MonkeyPatch, payload: dict, expected: list
) -> None:
    """Test a camera that has no recordings yields an empty list."""

    async def fake_get(
        _self: SpaceMonkeyDvr, _path: str, **_params: str
    ) -> JsonResponse:
        return JsonResponse(payload)

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    assert await dvr.get_recordings(27) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        ["not", "an", "object"],
        {"Ranges": {}},
        {"Ranges": ""},
        {"Ranges": 0},
        {"Ranges": False},
        {"Ranges": [{"Id": "x"}]},
        {"Ranges": [{"Id": "x", "CameraId": 1, "StartTime": "a", "EndTime": 2}]},
    ],
)
async def test_get_recordings_rejects_malformed_response(
    monkeypatch: pytest.MonkeyPatch, payload: Any
) -> None:
    """Test an unexpected recordings response is reported as a DVR error."""

    async def fake_get(
        _self: SpaceMonkeyDvr, _path: str, **_params: str
    ) -> JsonResponse:
        return JsonResponse(payload)

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    with pytest.raises(SpaceMonkeyError, match="Unexpected recordings"):
        await dvr.get_recordings(27)


def current_dvr(system: System) -> SpaceMonkeyDvr | None:
    """Return the DVR of a system, which changes as the system is refreshed."""
    return system.dvr


def system_data(dvr_service_id: str | None) -> dict:
    """Return the data of a system, optionally with a DVR service."""
    services = [{"t": "SPMO_DVR", "exid": dvr_service_id}] if dvr_service_id else []
    return {
        "system": {
            "panid": 1,
            "par": [{"panid": 1, "parid": 1, "d": []}],
            "u": [],
            "srvs": services,
        }
    }


@pytest.mark.asyncio
async def test_system_refresh_follows_the_dvr_service() -> None:
    """Test a refresh creates, keeps, replaces and drops the DVR as the service changes."""

    class Api:
        data = system_data(None)

        async def get_system_data(self, _panel_id: int) -> dict:
            return self.data

    api = Api()
    system = System(api.data, api, name="Home", is_admin=True)  # type: ignore[arg-type]
    assert current_dvr(system) is None

    api.data = system_data("first")
    await system.refresh()
    first = current_dvr(system)
    assert first and first.dvr_service_id == "first"

    await system.refresh()
    assert current_dvr(system) is first

    api.data = system_data("second")
    await system.refresh()
    second = current_dvr(system)
    assert second and second.dvr_service_id == "second"
    assert second is not first

    api.data = system_data(None)
    await system.refresh()
    assert current_dvr(system) is None


@pytest.mark.asyncio
async def test_account_disconnect_survives_a_failing_dvr() -> None:
    """Test every DVR is disconnected and the API is closed even if one DVR fails."""
    closed: list[str] = []

    class Dvr:
        def __init__(self, name: str, fail: bool) -> None:
            self.name, self.fail = name, fail

        async def disconnect(self) -> None:
            closed.append(self.name)
            if self.fail:
                raise RuntimeError("boom")

    class Api:
        async def disconnect(self) -> None:
            closed.append("api")

    account = Account("user", "password", client_session=MagicMock())
    account._api = Api()  # type: ignore[assignment]  # pylint: disable=protected-access
    account.systems = [
        SimpleNamespace(dvr=Dvr("one", True)),  # type: ignore[list-item]
        SimpleNamespace(dvr=None),  # type: ignore[list-item]
        SimpleNamespace(dvr=Dvr("two", False)),  # type: ignore[list-item]
    ]

    await account.disconnect()

    assert sorted(closed) == ["api", "one", "two"]


@pytest.mark.asyncio
async def test_system_refresh_survives_a_failing_dvr_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR that fails to close neither aborts the refresh nor is forgotten."""

    class Api:
        data = system_data("first")

        async def get_system_data(self, _panel_id: int) -> dict:
            return self.data

    api = Api()
    system = System(api.data, api, name="Home", is_admin=True)  # type: ignore[arg-type]
    first = current_dvr(system)
    assert first

    attempts = 0

    async def failing_disconnect(_self: SpaceMonkeyDvr) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("boom")

    monkeypatch.setattr(SpaceMonkeyDvr, "disconnect", failing_disconnect)

    api.data = system_data("second")
    api.data["system"]["par"][0]["d"] = []
    await system.refresh()  # must not raise
    second = current_dvr(system)
    assert second and second.dvr_service_id == "second"
    assert attempts == 1

    await system.refresh()  # retries the cleanup of the first DVR
    assert attempts == 2
    await system.refresh()  # nothing left to retry
    assert attempts == 2

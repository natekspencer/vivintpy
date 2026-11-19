"""Test the Space Monkey DVR client."""

from __future__ import annotations

import asyncio
import base64
import json
import ssl
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any, Self
from unittest.mock import MagicMock

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import ClientOSError, ClientSession, ContentTypeError, CookieJar, web
from aiohttp.test_utils import TestServer
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from vivintpy import spacemonkey
from vivintpy.account import Account
from vivintpy.exceptions import (
    SpaceMonkeyError,
    VivintSkyApiAuthenticationError,
    VivintSkyApiError,
    VivintSkyApiMfaRequiredError,
)
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
    """Return an X.509 name with the given common name."""
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def _certificate(
    subject: str, issuer: str, key: Any, signer: Any, *, ca: bool
) -> x509.Certificate:
    """Return a certificate for the subject, signed with the signer's key."""
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
        """Accept the authorization code and start a Space Monkey session."""
        calls["paths"].append(request.path)
        calls["code"] = request.query.get("code")
        response = web.json_response({"response": {"message": "Success"}})
        response.set_cookie("session", "abc")
        return response

    async def certs(request: web.Request) -> web.Response:
        """Return the client certificate bundle for the requested DVR service."""
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
        """Return where the DVR is on the local network."""
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
            """Enter the response context."""
            return self

        async def __aexit__(self, *_args: object) -> None:
            """Leave the response context."""
            return

        async def json(self) -> dict:
            """Return the canned payload."""
            return payload

    async def fake_get(_self: SpaceMonkeyDvr, path: str, **params: str) -> FakeResponse:
        """Record the request and return a canned response."""
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
        """Keep the payload to return."""
        self._payload = payload

    async def __aenter__(self) -> Self:
        """Enter the response context."""
        return self

    async def __aexit__(self, *_args: object) -> None:
        """Leave the response context."""
        return

    async def json(self) -> Any:
        """Return the payload, or raise it if it is an exception."""
        if isinstance(self._payload, Exception):
            raise self._payload
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
        """Return the canned payload instead of asking the DVR."""
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
        """Return the canned payload instead of asking the DVR."""
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
            """Return the current system data."""
            return self.data

        async def get_climate_devices(self, _system_id: int) -> list:
            """Return no thermostats."""
            return []

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


def make_system(dvr_service_id: str | None) -> System:
    """Return a system whose API is never called."""
    return System(
        system_data(dvr_service_id),
        None,  # type: ignore[arg-type]
        name="Home",
        is_admin=True,
    )


@pytest.mark.asyncio
async def test_account_disconnect_survives_a_failing_dvr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test every DVR, replaced ones included, is disconnected even if one fails."""
    closed: list[str] = []

    async def disconnect(self: SpaceMonkeyDvr) -> None:
        """Record the disconnect, failing for the DVR named one."""
        closed.append(self.dvr_service_id)
        if self.dvr_service_id == "one":
            raise RuntimeError("boom")

    monkeypatch.setattr(SpaceMonkeyDvr, "disconnect", disconnect)

    class Api:
        async def disconnect(self) -> None:
            """Record that the API was closed."""
            closed.append("api")

    account = Account("user", "password", client_session=MagicMock())
    account._api = Api()  # type: ignore[assignment]  # pylint: disable=protected-access
    stale = make_system("stale")
    stale._stale_dvrs.append(SpaceMonkeyDvr(None, "replaced"))  # type: ignore[arg-type]  # pylint: disable=protected-access
    account.systems = [make_system("one"), make_system(None), make_system("two"), stale]

    await account.disconnect()

    assert sorted(closed) == ["api", "one", "replaced", "stale", "two"]


@pytest.mark.asyncio
async def test_overlapping_cleanups_keep_every_failed_dvr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR queued while others are being closed is neither lost nor miscounted."""
    system = make_system(None)
    release = asyncio.Event()
    attempts: list[str] = []

    async def disconnect(self: SpaceMonkeyDvr) -> None:
        """Record the attempt; the first DVR waits to be released and then fails."""
        attempts.append(self.dvr_service_id)
        if self.dvr_service_id == "first":
            await release.wait()
            raise RuntimeError("boom")

    monkeypatch.setattr(SpaceMonkeyDvr, "disconnect", disconnect)
    first = SpaceMonkeyDvr(None, "first")  # type: ignore[arg-type]
    system._stale_dvrs.append(first)  # pylint: disable=protected-access

    cleanup = asyncio.create_task(system._close_stale_dvrs())  # pylint: disable=protected-access
    await asyncio.sleep(0)
    second = SpaceMonkeyDvr(None, "second")  # type: ignore[arg-type]
    system._stale_dvrs.append(second)  # pylint: disable=protected-access
    release.set()
    await cleanup

    assert system._stale_dvrs == [first, second]  # pylint: disable=protected-access
    assert attempts == ["first"]


@pytest.mark.asyncio
async def test_system_refresh_survives_a_failing_dvr_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR that fails to close neither aborts the refresh nor is forgotten."""

    class Api:
        data = system_data("first")

        async def get_system_data(self, _panel_id: int) -> dict:
            """Return the current system data."""
            return self.data

        async def get_climate_devices(self, _system_id: int) -> list:
            """Return no thermostats."""
            return []

    api = Api()
    system = System(api.data, api, name="Home", is_admin=True)  # type: ignore[arg-type]
    first = current_dvr(system)
    assert first

    attempts = 0

    async def failing_disconnect(_self: SpaceMonkeyDvr) -> None:
        """Fail the first attempt only."""
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


NOT_JSON = [
    ContentTypeError(MagicMock(), (), message="Attempt to decode JSON"),
    json.JSONDecodeError("Expecting value", "", 0),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("error", NOT_JSON)
@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda dvr: dvr.get_status(), "Unexpected status"),
        (lambda dvr: dvr.get_recordings(27), "Unexpected recordings"),
    ],
)
async def test_dvr_responses_that_are_not_json(
    monkeypatch: pytest.MonkeyPatch, error: Exception, call: Any, message: str
) -> None:
    """Test a DVR response without a JSON body is reported as a DVR error."""

    async def fake_get(
        _self: SpaceMonkeyDvr, _path: str, **_params: str
    ) -> JsonResponse:
        """Return a response whose body cannot be parsed."""
        return JsonResponse(error)

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    with pytest.raises(SpaceMonkeyError, match=message):
        await call(dvr)


@pytest.mark.asyncio
async def test_status_must_be_an_object(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a status response that is not an object is reported as a DVR error."""

    async def fake_get(
        _self: SpaceMonkeyDvr, _path: str, **_params: str
    ) -> JsonResponse:
        """Return a status that is a list."""
        return JsonResponse([])

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    with pytest.raises(SpaceMonkeyError, match="Unexpected status"):
        await dvr.get_status()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        ("<html></html>", "text/html"),
        ("not json", "application/json"),
        ("[]", "application/json"),
        ('{"address": "nowhere"}', "application/json"),
    ],
)
@pytest.mark.parametrize(
    ("renew", "message"),
    [(True, "Unexpected certificate"), (False, "Unexpected directory")],
)
async def test_cloud_responses_that_are_not_usable(
    monkeypatch: pytest.MonkeyPatch,
    body: str,
    content_type: str,
    renew: bool,
    message: str,
) -> None:
    """Test unusable certificate and directory responses are reported as DVR errors."""

    async def respond(_request: web.Request) -> web.Response:
        """Return the same unusable body for every request."""
        return web.Response(text=body, content_type=content_type)

    async def authorized(_request: web.Request) -> web.Response:
        """Accept the authorization code."""
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_get("/authorized", authorized)
    app.router.add_get("/v2/playback/certs", respond)
    app.router.add_get(f"/directory/mm/entry/hardware/{HARDWARE_ID}", respond)
    server = TestServer(app)
    await server.start_server()
    base = str(server.make_url("")).rstrip("/")
    monkeypatch.setattr(spacemonkey, "ACCOUNTS_ENDPOINT", base)
    monkeypatch.setattr(spacemonkey, "REDIRECT_URI", f"{base}/authorized")
    monkeypatch.setattr(spacemonkey, "DIRECTORY_ENDPOINT", base)
    try:
        async with ClientSession() as session:
            dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
            dvr.hardware_id = HARDWARE_ID

            with pytest.raises(SpaceMonkeyError, match=message):
                if renew:
                    await dvr._renew_certificate()  # pylint: disable=protected-access
                else:
                    await dvr._locate()  # pylint: disable=protected-access
    finally:
        await server.close()


class FakeResponse:
    """A response with a status code."""

    def __init__(self, status: int) -> None:
        """Keep the status."""
        self.status = status
        self.released = False

    def release(self) -> None:
        """Record that the response was released."""
        self.released = True


class FakeSession:
    """A session that answers each request with the next canned outcome."""

    closed = False

    def __init__(self, *outcomes: int | Exception) -> None:
        """Keep the outcomes, which are status codes or exceptions to raise."""
        self.outcomes = list(outcomes)
        self.requests: list[tuple[str, dict[str, Any]]] = []

    async def get(self, url: str, **kwargs: Any) -> FakeResponse:
        """Record the request, then return or raise the next outcome."""
        self.requests.append((url, kwargs))
        await asyncio.sleep(0)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)


def connected_dvr(
    monkeypatch: pytest.MonkeyPatch, session: FakeSession
) -> tuple[SpaceMonkeyDvr, dict[str, int]]:
    """Return a connected DVR that uses the fake session and counts its lookups."""
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
    dvr._ssl_context = MagicMock()  # pylint: disable=protected-access
    dvr.address = spacemonkey.DvrAddress("dvr.example.test", 8080, "192.0.2.10")
    dvr.certificate_expiry = datetime.now(UTC) + timedelta(hours=24)
    counts = {"locate": 0, "renew": 0}

    async def locate(_self: SpaceMonkeyDvr) -> None:
        """Count a lookup."""
        counts["locate"] += 1

    async def renew(self: SpaceMonkeyDvr) -> None:
        """Count a renewal, which changes the expiry."""
        counts["renew"] += 1
        self.certificate_expiry = datetime.now(UTC) + timedelta(hours=24)

    monkeypatch.setattr(SpaceMonkeyDvr, "_locate", locate)
    monkeypatch.setattr(SpaceMonkeyDvr, "_renew_certificate", renew)
    return dvr, counts


@pytest.mark.asyncio
async def test_get_renews_the_certificate_after_a_401(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a 401 renews the certificate and the request is repeated."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(401, 200))

    resp = await dvr.get("/status")

    assert resp.status == 200
    assert counts == {"locate": 0, "renew": 1}


@pytest.mark.asyncio
async def test_get_connects_to_the_local_ip_and_verifies_the_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a request doesn't depend on DNS resolving the DVR's name."""
    session = FakeSession(200)
    dvr, _ = connected_dvr(monkeypatch, session)

    await dvr.get("/status")

    [(url, kwargs)] = session.requests
    assert url == "https://192.0.2.10:8080/status"
    assert kwargs["server_hostname"] == "dvr.example.test"
    assert kwargs["headers"] == {"Host": "dvr.example.test:8080"}


@pytest.mark.asyncio
async def test_get_brackets_an_ipv6_local_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an IPv6 address is written as a valid URL host."""
    session = FakeSession(200)
    dvr, _ = connected_dvr(monkeypatch, session)
    dvr.address = spacemonkey.DvrAddress("dvr.example.test", 8080, "2001:db8::10")

    await dvr.get("/status")

    assert session.requests[0][0] == "https://[2001:db8::10]:8080/status"


@pytest.mark.asyncio
async def test_get_gives_up_after_a_second_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a certificate that is still refused is reported."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(401, 401))

    with pytest.raises(SpaceMonkeyError, match="HTTP 401"):
        await dvr.get("/status")

    assert counts["renew"] == 1


@pytest.mark.asyncio
async def test_get_reports_other_statuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a status other than 200 is reported."""
    dvr, _ = connected_dvr(monkeypatch, FakeSession(404))

    with pytest.raises(SpaceMonkeyError, match="HTTP 404"):
        await dvr.get("/status")


@pytest.mark.asyncio
async def test_get_looks_the_dvr_up_again_when_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a connection failure is retried after locating the DVR again."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(ClientOSError(), 200))

    await dvr.get("/status")

    assert counts == {"locate": 1, "renew": 0}


@pytest.mark.asyncio
async def test_get_renews_a_certificate_the_dvr_drops(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a connection that keeps failing is retried with a new certificate."""
    session = FakeSession(ClientOSError(), ClientOSError(), 200)
    dvr, counts = connected_dvr(monkeypatch, session)

    await dvr.get("/status")

    assert counts == {"locate": 1, "renew": 1}


@pytest.mark.asyncio
async def test_get_gives_up_when_the_dvr_stays_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR that cannot be reached is reported."""
    session = FakeSession(ClientOSError(), ClientOSError(), ClientOSError())
    dvr, _ = connected_dvr(monkeypatch, session)

    with pytest.raises(SpaceMonkeyError, match="Unable to reach"):
        await dvr.get("/status")


@pytest.mark.asyncio
async def test_concurrent_401s_renew_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test requests refused together share one renewal."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(401, 401, 200, 200))

    await asyncio.gather(dvr.get("/a"), dvr.get("/b"))

    assert counts["renew"] == 1


@pytest.mark.asyncio
async def test_disconnected_dvr_is_not_reopened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a disconnected DVR refuses requests instead of opening a session."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession())

    await dvr.disconnect()

    with pytest.raises(SpaceMonkeyError, match="disconnected"):
        await dvr.get("/status")
    assert counts == {"locate": 0, "renew": 0}


@pytest.mark.asyncio
async def test_disconnect_during_a_request_is_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR disconnected while a request is retried reports it."""
    dvr, _ = connected_dvr(monkeypatch, FakeSession(ClientOSError()))

    async def locate(self: SpaceMonkeyDvr) -> None:
        """Disconnect while the DVR is being looked up."""
        self._closed = True  # pylint: disable=protected-access
        self._session = None  # pylint: disable=protected-access

    monkeypatch.setattr(SpaceMonkeyDvr, "_locate", locate)

    with pytest.raises(SpaceMonkeyError, match="disconnected"):
        await dvr.get("/status")


@pytest.mark.asyncio
async def test_network_errors_while_connecting_are_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a failure to reach the cloud is reported as a DVR error."""
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]
    dvr.hardware_id = HARDWARE_ID
    monkeypatch.setattr(spacemonkey, "DIRECTORY_ENDPOINT", "http://127.0.0.1:1")

    with pytest.raises(SpaceMonkeyError):
        await dvr._locate()  # pylint: disable=protected-access
    await dvr.disconnect()


@pytest.mark.asyncio
async def test_certificate_expiry_without_offset_is_utc(
    bundle: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test an expiry without a UTC offset is read as UTC."""
    expires = (datetime.now(UTC) + timedelta(hours=24)).replace(tzinfo=None)

    async def authorized(_request: web.Request) -> web.Response:
        """Accept the authorization code."""
        return web.Response(text="ok")

    async def certs(_request: web.Request) -> web.Response:
        """Return a certificate whose expiry has no offset."""
        return web.json_response(
            {
                "pkcs12_b64": base64.b64encode(bundle).decode(),
                "hw_id": HARDWARE_ID,
                "expires_at": expires.isoformat(),
            }
        )

    app = web.Application()
    app.router.add_get("/authorized", authorized)
    app.router.add_get("/v2/playback/certs", certs)
    server = TestServer(app)
    await server.start_server()
    base = str(server.make_url("")).rstrip("/")
    monkeypatch.setattr(spacemonkey, "ACCOUNTS_ENDPOINT", base)
    monkeypatch.setattr(spacemonkey, "REDIRECT_URI", f"{base}/authorized")
    try:
        async with ClientSession() as session:
            dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]

            await dvr._renew_certificate()  # pylint: disable=protected-access

            assert dvr.certificate_expiry == expires.replace(tzinfo=UTC)
    finally:
        await server.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", [401, ClientOSError()])
async def test_disconnect_while_waiting_for_the_lock_stops_the_retry(
    monkeypatch: pytest.MonkeyPatch, outcome: int | Exception
) -> None:
    """Test a request that waited out a disconnect does not locate or renew."""
    session = FakeSession(outcome)
    dvr, counts = connected_dvr(monkeypatch, session)
    disconnecting: list[asyncio.Task[None]] = []

    async def disconnect_slowly() -> None:
        """Hold the lock while disconnecting."""
        async with dvr._lock:  # pylint: disable=protected-access
            await asyncio.sleep(0.01)
            dvr._closed = True  # pylint: disable=protected-access
            dvr._session = None  # pylint: disable=protected-access

    original_get = session.get

    async def get(url: str, **kwargs: Any) -> FakeResponse:
        """Start the disconnect as the request is answered."""
        disconnecting.append(asyncio.ensure_future(disconnect_slowly()))
        await asyncio.sleep(0)
        return await original_get(url, **kwargs)

    session.get = get  # type: ignore[method-assign]

    with pytest.raises(SpaceMonkeyError, match="disconnected"):
        await dvr.get("/status")
    await asyncio.gather(*disconnecting)
    assert counts == {"locate": 0, "renew": 0}


def test_find_dvr_service_id_tolerates_missing_data() -> None:
    """Test null services and entries without an id are skipped."""
    assert find_dvr_service_id({"system": {"srvs": None}}) is None
    assert find_dvr_service_id({"system": None}) is None
    data = {
        "system": {
            "srvs": [{"t": "SPMO_DVR"}, {"t": "SPMO_DVR", "exid": "dvr-id"}],
        }
    }
    assert find_dvr_service_id(data) == "dvr-id"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        aiohttp.ConnectionTimeoutError(),
        aiohttp.ClientConnectionResetError(),
        TimeoutError(),
    ],
)
async def test_get_looks_the_dvr_up_again_after_a_timeout(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    """Test timeouts and resets are retried like other connection failures."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(error, 200))

    await dvr.get("/status")

    assert counts == {"locate": 1, "renew": 0}


class FailingBody:
    """A response whose body fails while being read."""

    def __init__(self, error: Exception) -> None:
        """Keep the error to raise."""
        self._error = error
        self.content = self

    async def __aenter__(self) -> Self:
        """Enter the response context."""
        return self

    async def __aexit__(self, *_args: object) -> None:
        """Leave the response context."""
        return

    def iter_chunked(self, _size: int) -> Self:
        """Return the chunk iterator."""
        return self

    def __aiter__(self) -> Self:
        """Iterate over the chunks."""
        return self

    async def __anext__(self) -> bytes:
        """Fail instead of returning a chunk."""
        raise self._error

    async def text(self) -> str:
        """Fail instead of returning the text."""
        raise self._error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        aiohttp.ClientPayloadError(),
        TimeoutError(),
        UnicodeDecodeError("utf-8", b"", 0, 1, "bad"),
    ],
)
async def test_errors_reading_a_body_are_reported(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    """Test failures while reading a response body are DVR errors."""

    async def fake_get(_self: SpaceMonkeyDvr, _path: str, **_params: str) -> Any:
        """Return a response whose body fails."""
        return FailingBody(error)

    monkeypatch.setattr(SpaceMonkeyDvr, "get", fake_get)
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]

    with pytest.raises(SpaceMonkeyError):
        await dvr.get_playlist(1, "rec")
    if not isinstance(error, UnicodeDecodeError):
        with pytest.raises(SpaceMonkeyError):
            async for _ in dvr.stream_segment(1, "rec", 1):
                pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        VivintSkyApiAuthenticationError("nope"),
        VivintSkyApiError("down"),
        VivintSkyApiMfaRequiredError("mfa"),
    ],
)
async def test_vivint_errors_while_renewing_are_reported(error: Exception) -> None:
    """Test Vivint errors during renewal are DVR errors."""

    class RaisingApi:
        """An API that cannot hand out a code."""

        async def get_authorization_code(self, *_args: Any, **_kwargs: Any) -> str:
            """Raise the error."""
            raise error

    dvr = SpaceMonkeyDvr(RaisingApi(), "dvr-id")  # type: ignore[arg-type]

    with pytest.raises(SpaceMonkeyError):
        await dvr.connect()
    await dvr.disconnect()


@pytest.mark.asyncio
async def test_failed_early_renewal_keeps_the_valid_certificate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a renewal that fails before expiry doesn't fail the request."""
    dvr, _ = connected_dvr(monkeypatch, FakeSession(200))
    dvr.certificate_expiry = datetime.now(UTC) + timedelta(minutes=10)

    async def renew(_self: SpaceMonkeyDvr) -> None:
        """Fail to renew."""
        raise SpaceMonkeyError("outage")

    monkeypatch.setattr(SpaceMonkeyDvr, "_renew_certificate", renew)

    await dvr.get("/status")

    dvr.certificate_expiry = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(SpaceMonkeyError, match="outage"):
        await dvr.get("/status")


@pytest.mark.asyncio
async def test_failed_early_renewal_backs_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a failed early renewal isn't retried until the interval passes."""
    dvr, _ = connected_dvr(monkeypatch, FakeSession(200, 200, 200))
    dvr.certificate_expiry = datetime.now(UTC) + timedelta(minutes=10)
    attempts = 0

    async def renew(_self: SpaceMonkeyDvr) -> None:
        """Fail to renew."""
        nonlocal attempts
        attempts += 1
        raise SpaceMonkeyError("outage")

    monkeypatch.setattr(SpaceMonkeyDvr, "_renew_certificate", renew)

    await dvr.get("/status")
    await dvr.get("/status")
    assert attempts == 1

    dvr._renew_failed_at = datetime.now(UTC) - timedelta(minutes=6)  # pylint: disable=protected-access
    await dvr.get("/status")
    assert attempts == 2


@pytest.mark.asyncio
async def test_failed_close_can_be_retried() -> None:
    """Test the session is kept when closing it fails."""
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id")  # type: ignore[arg-type]
    session = MagicMock()
    session.closed = False
    session.close = MagicMock(side_effect=[RuntimeError("boom"), _done()])
    dvr._session = session  # pylint: disable=protected-access

    with pytest.raises(RuntimeError):
        await dvr.disconnect()
    assert dvr._session is session  # pylint: disable=protected-access

    await dvr.disconnect()
    assert dvr._session is None  # pylint: disable=protected-access


def _done() -> Any:
    """Return an awaitable that completes immediately."""
    future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
    future.set_result(None)
    return future


@pytest.mark.asyncio
async def test_closed_supplied_session_is_reported() -> None:
    """Test a closed caller-supplied session raises a DVR error."""
    session = ClientSession()
    await session.close()
    dvr = SpaceMonkeyDvr(FakeApi(), "dvr-id", session)  # type: ignore[arg-type]
    dvr._ssl_context = MagicMock()  # pylint: disable=protected-access
    dvr.address = spacemonkey.DvrAddress("dvr.example.test", 8080, "192.0.2.10")
    dvr.certificate_expiry = datetime.now(UTC) + timedelta(hours=24)

    with pytest.raises(SpaceMonkeyError, match="closed"):
        await dvr.get("/status")


@pytest.mark.asyncio
async def test_cancelled_cleanup_keeps_the_stale_dvrs() -> None:
    """Test cancelling a cleanup doesn't lose the DVRs being closed."""
    system = make_system(None)
    stale = SpaceMonkeyDvr(None, "stale")  # type: ignore[arg-type]
    system._stale_dvrs.append(stale)  # pylint: disable=protected-access

    async def hang(_self: SpaceMonkeyDvr) -> None:
        """Never finish closing."""
        await asyncio.sleep(3600)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(SpaceMonkeyDvr, "disconnect", hang)
        task = asyncio.create_task(system._close_stale_dvrs())  # pylint: disable=protected-access
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    assert system._stale_dvrs == [stale]  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_failed_disconnect_does_not_stale_the_current_dvr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR that failed to close isn't disconnected again by a later refresh."""
    system = make_system("dvr-id")

    async def disconnect(_self: SpaceMonkeyDvr) -> None:
        """Fail to close."""
        raise RuntimeError("boom")

    monkeypatch.setattr(SpaceMonkeyDvr, "disconnect", disconnect)

    await system.disconnect_dvrs()

    assert system._stale_dvrs == []  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_get_uses_a_short_connect_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR that doesn't answer is reported without the default 30 seconds."""
    session = FakeSession(200)
    dvr, _ = connected_dvr(monkeypatch, session)

    await dvr.get("/status")

    timeout = session.requests[0][1]["timeout"]
    assert timeout is spacemonkey.DVR_TIMEOUT
    assert timeout.connect == 5
    assert timeout.sock_connect == 5
    assert timeout.sock_read == 30
    assert timeout.total is None


@pytest.mark.asyncio
async def test_failed_lookup_does_not_renew_the_certificate_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a DVR with a valid certificate that isn't located is only looked up."""
    session = FakeSession(200, 200)
    dvr, counts = connected_dvr(monkeypatch, session)
    dvr.address = None

    async def locate(self: SpaceMonkeyDvr) -> None:
        """Fail once, as a directory that is briefly down does, then succeed."""
        counts["locate"] += 1
        if counts["locate"] == 1:
            raise SpaceMonkeyError("Directory lookup failed: 503")
        self.address = spacemonkey.DvrAddress("dvr.example.test", 8080, "192.0.2.10")

    monkeypatch.setattr(SpaceMonkeyDvr, "_locate", locate)

    with pytest.raises(SpaceMonkeyError, match="Directory lookup"):
        await dvr.get("/status")
    await dvr.get("/status")

    assert counts == {"locate": 2, "renew": 0}


@pytest.mark.asyncio
async def test_get_does_not_renew_again_after_a_renewed_certificate_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test requests made one after another don't each sign in again."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(401, 401, 401, 401))

    for _ in range(3):
        with pytest.raises(SpaceMonkeyError, match="HTTP 401"):
            await dvr.get("/status")

    assert counts["renew"] == 1


@pytest.mark.asyncio
async def test_get_renews_after_a_refusal_once_the_interval_has_passed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a refused certificate is tried again after the retry interval."""
    dvr, counts = connected_dvr(monkeypatch, FakeSession(401, 401, 401, 200))

    with pytest.raises(SpaceMonkeyError, match="HTTP 401"):
        await dvr.get("/status")
    dvr._rejected_at = (  # pylint: disable=protected-access
        datetime.now(UTC) - spacemonkey.RENEW_RETRY_INTERVAL - timedelta(seconds=1)
    )

    resp = await dvr.get("/status")

    assert resp.status == 200
    assert counts["renew"] == 2

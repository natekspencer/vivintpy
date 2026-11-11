"""Module that implements access to the Space Monkey DVR attached to a Vivint system."""

from __future__ import annotations

import asyncio
import base64
import functools
import logging
import os
import re
import ssl
import tempfile
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, cast

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from .exceptions import SpaceMonkeyError, VivintError
from .utils import from_microseconds

if TYPE_CHECKING:
    from .api import VivintSkyApi

_LOGGER = logging.getLogger(__name__)

_P = ParamSpec("_P")
_T = TypeVar("_T")

ACCOUNTS_ENDPOINT = "https://accounts.spacemonkey.com"
DIRECTORY_ENDPOINT = "https://directory.spacemonkey.com"
CLIENT_ID = "6af9ddae12d490ea76d9f30fa74e66f3"
REALM = "smas"
REDIRECT_URI = f"{ACCOUNTS_ENDPOINT}/users/vivint/authorized"
DVR_SERVICE_TYPE = "SPMO_DVR"

# Certificates last 24 hours; renew well before the DVR starts rejecting them.
RENEW_MARGIN = timedelta(minutes=30)
RENEW_RETRY_INTERVAL = timedelta(minutes=5)

# The DVR is on the local network, so a DVR that doesn't answer is reported quickly;
# sock_read keeps a stalled segment stream from hanging without capping a download.
DVR_TIMEOUT = aiohttp.ClientTimeout(sock_connect=5, sock_read=30)

_EXTINF = re.compile(r"#EXTINF:([\d.]+),")
_SEGMENT_NUMBER = re.compile(r"(\d+)\.ts$")


@dataclass(frozen=True)
class DvrRecording:
    """A contiguous range of recorded video for one camera."""

    id: str
    camera_id: int
    start: datetime
    end: datetime


@dataclass(frozen=True)
class DvrSegment:
    """One MPEG-TS segment of a recording; `number` starts at 1."""

    recording_id: str
    number: int
    start: datetime
    duration: float

    @property
    def end(self) -> datetime:
        """Return when the segment ends."""
        return self.start + timedelta(seconds=self.duration)


@dataclass(frozen=True)
class DvrAddress:
    """Where the DVR can be reached on the local network."""

    host: str
    port: int
    local_ip: str


def find_dvr_service_id(system_data: dict[str, Any]) -> str | None:
    """Return the DVR service id from a system's data, if the system has a DVR."""
    for service in (system_data.get("system") or {}).get("srvs") or []:
        if service.get("t") == DVR_SERVICE_TYPE and (exid := service.get("exid")):
            return cast("str", exid)
    return None


def parse_playlist(playlist: str, recording: DvrRecording) -> list[DvrSegment]:
    """Place every segment of an HLS playlist on the recording's timeline."""
    segments: list[DvrSegment] = []
    elapsed = 0.0
    duration: float | None = None
    for line in playlist.splitlines():
        if match := _EXTINF.match(line):
            duration = float(match.group(1))
        elif duration is not None and (number := _SEGMENT_NUMBER.search(line)):
            segments.append(
                DvrSegment(
                    recording.id,
                    int(number.group(1)),
                    recording.start + timedelta(seconds=elapsed),
                    duration,
                )
            )
            elapsed += duration
            duration = None
    return segments


def _dvr_errors(
    func: Callable[_P, Awaitable[_T]],
) -> Callable[_P, Awaitable[_T]]:
    """Report network failures of a coroutine as `SpaceMonkeyError`."""

    @functools.wraps(func)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        """Run the coroutine."""
        try:
            return await func(*args, **kwargs)
        except SpaceMonkeyError:
            raise
        except (
            aiohttp.ClientError,
            TimeoutError,
            UnicodeDecodeError,
            VivintError,
        ) as err:
            raise SpaceMonkeyError(f"{func.__name__.strip('_')} failed: {err}") from err

    return wrapper


async def _read_json(resp: aiohttp.ClientResponse, what: str) -> Any:
    """Return the JSON body of a response, raising `SpaceMonkeyError` if it has none."""
    try:
        return await resp.json()
    except (aiohttp.ContentTypeError, ValueError) as err:
        raise SpaceMonkeyError(f"Unexpected {what} response") from err


def _build_ssl_context(pkcs12_bytes: bytes) -> ssl.SSLContext:
    """Build a TLS context that presents the client certificate to the DVR."""
    try:
        key, cert, chain = pkcs12.load_key_and_certificates(pkcs12_bytes, b"")
    except ValueError as err:
        raise SpaceMonkeyError("The certificate bundle could not be read") from err
    if key is None or cert is None:
        raise SpaceMonkeyError("The certificate bundle is missing its key or leaf")
    if not chain:
        raise SpaceMonkeyError("The certificate bundle is missing its authorities")
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ) + cert.public_bytes(serialization.Encoding.PEM)
    authorities = "".join(
        c.public_bytes(serialization.Encoding.PEM).decode() for c in chain
    )

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    try:
        # The DVR issues 1024-bit client keys, which OpenSSL rejects at its default
        # security level. The relaxation only applies to connections made with this
        # context.
        context.set_ciphers("DEFAULT:@SECLEVEL=1")
        # The device certificate is signed by Space Monkey's private CA, which is
        # delivered together with the client certificate.
        context.load_verify_locations(cadata=authorities)
        # load_cert_chain only accepts a file path.
        fd, path = tempfile.mkstemp(suffix=".pem")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(pem)
            context.load_cert_chain(path)
        finally:
            os.unlink(path)
    except ssl.SSLError as err:
        raise SpaceMonkeyError("The certificate bundle could not be used") from err
    return context


class SpaceMonkeyDvr:
    """
    Class for talking to the Space Monkey DVR that stores a system's recordings.

    The DVR only accepts clients with a short-lived certificate, which is issued to
    the signed-in Vivint account. The certificate is renewed automatically.
    """

    def __init__(
        self,
        api: VivintSkyApi,
        dvr_service_id: str,
        client_session: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        Initialize the DVR.

        A supplied client session must keep cookies, as Space Monkey's session is
        carried in one, and it is not closed by `disconnect`.
        """
        self._api = api
        self._dvr_service_id = dvr_service_id
        self._session = client_session
        self._owns_session = client_session is None
        self._ssl_context: ssl.SSLContext | None = None
        self._lock = asyncio.Lock()
        self._closed = False
        self.hardware_id: str | None = None
        self.certificate_expiry: datetime | None = None
        self._renew_failed_at: datetime | None = None
        self._rejected_at: datetime | None = None
        self.address: DvrAddress | None = None

    @classmethod
    def from_system_data(
        cls,
        api: VivintSkyApi,
        system_data: dict[str, Any],
        client_session: aiohttp.ClientSession | None = None,
    ) -> SpaceMonkeyDvr | None:
        """Create the DVR for a system, or return None if the system has none."""
        if dvr_service_id := find_dvr_service_id(system_data):
            return cls(api, dvr_service_id, client_session)
        return None

    @property
    def dvr_service_id(self) -> str:
        """Return the id of the DVR service this client talks to."""
        return self._dvr_service_id

    @property
    def connected(self) -> bool:
        """Return True if the DVR has been located and a certificate is loaded."""
        return self._ssl_context is not None and self.address is not None

    async def connect(self) -> None:
        """Sign in to Space Monkey, get a certificate and locate the DVR."""
        async with self._lock:
            self._closed = False
            self._rejected_at = None
            await self._renew_certificate()
            await self._locate()

    async def disconnect(self) -> None:
        """
        Close the session if it was created by this object.

        Requests made afterwards fail until `connect` is called again.
        """
        async with self._lock:
            self._closed = True
            self._ssl_context = None
            session = self._session
            if self._owns_session and session:
                # Cleared only once closed, so a failed close can be retried
                if not session.closed:
                    await session.close()
                self._session = None

    @_dvr_errors
    async def get_status(self) -> dict[str, Any]:
        """Return the DVR's status, which includes its cameras."""
        async with await self.get("/web/v1/status") as resp:
            data = await _read_json(resp, "status")
        if not isinstance(data, dict):
            raise SpaceMonkeyError("Unexpected status response")
        return data

    @_dvr_errors
    async def get_recordings(self, camera_id: int) -> list[DvrRecording]:
        """Return the recorded ranges stored for a camera, oldest first."""
        async with await self.get("/recordings", camera=f"Video-{camera_id}") as resp:
            data = await _read_json(resp, "recordings")
        try:
            ranges = data.get("Ranges")
            if ranges is None:
                return []
            if not isinstance(ranges, list):
                raise TypeError("Ranges is not a list")
            return [
                DvrRecording(
                    id=item["Id"],
                    camera_id=item["CameraId"],
                    start=from_microseconds(item["StartTime"]),
                    end=from_microseconds(item["EndTime"]),
                )
                for item in ranges
            ]
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as err:
            raise SpaceMonkeyError("Unexpected recordings response") from err

    @_dvr_errors
    async def get_playlist(self, camera_id: int, recording_id: str) -> str:
        """Return the HLS playlist for a recorded range."""
        async with await self.get(
            f"/camstreams/Video-{camera_id}/{recording_id}/stream.m3u8"
        ) as resp:
            return str(await resp.text())

    async def stream_segment(
        self, camera_id: int, recording_id: str, number: int
    ) -> AsyncIterator[bytes]:
        """Stream the bytes of one MPEG-TS segment."""
        async with await self.get(
            f"/camstreams/Video-{camera_id}/{recording_id}/stream{number}.ts"
        ) as resp:
            try:
                async for chunk in resp.content.iter_chunked(1 << 16):
                    yield chunk
            except (aiohttp.ClientError, TimeoutError) as err:
                raise SpaceMonkeyError(f"stream_segment failed: {err}") from err

    async def get(self, path: str, **params: str) -> aiohttp.ClientResponse:
        """
        Make a GET request to the DVR; the caller must release the response.

        Renews the certificate when it is about to expire and looks the DVR up again
        if it cannot be reached.
        """
        await self._ensure_connected()
        located = renewed = False
        while True:
            session, address = self._session, self.address
            self._ensure_open()
            if session is None or address is None:
                raise SpaceMonkeyError("The DVR has been disconnected")
            if session.closed:
                raise SpaceMonkeyError("The client session has been closed")
            seen_expiry = self.certificate_expiry
            # The DVR's name doesn't resolve on every network, so connect to its
            # local IP and verify the certificate against the name instead
            ip = (
                f"[{address.local_ip}]" if ":" in address.local_ip else address.local_ip
            )
            url = f"https://{ip}:{address.port}{path}"
            try:
                resp = await session.get(
                    url,
                    params=params or None,
                    ssl=self._ssl_context,
                    server_hostname=address.host,
                    headers={"Host": f"{address.host}:{address.port}"},
                    timeout=DVR_TIMEOUT,
                )
            except (aiohttp.ClientConnectionError, TimeoutError) as err:
                # A DVR that rejects the certificate drops the connection during the
                # TLS handshake, and one that moved stops answering, so a connection
                # failure is retried after looking the DVR up again and then after
                # renewing the certificate.
                if not located:
                    located = True
                    async with self._lock:
                        self._ensure_open()
                        await self._locate()
                elif not renewed:
                    renewed = True
                    await self._renew_if_unchanged(seen_expiry)
                else:
                    raise SpaceMonkeyError(f"Unable to reach the DVR: {err}") from err
                continue
            except aiohttp.ClientError as err:
                raise SpaceMonkeyError(f"DVR request failed: {err}") from err

            if resp.status == 401:
                resp.release()
                if (
                    not renewed
                    and self._rejected_at is not None
                    and datetime.now(UTC) - self._rejected_at < RENEW_RETRY_INTERVAL
                ):
                    # A renewal just now was refused too, so don't sign in again
                    raise SpaceMonkeyError(f"{path} returned HTTP 401")
                if not renewed:
                    renewed = True
                    await self._renew_if_unchanged(seen_expiry)
                    continue
                self._rejected_at = datetime.now(UTC)
                raise SpaceMonkeyError(f"{path} returned HTTP 401")
            if resp.status != 200:
                resp.release()
                raise SpaceMonkeyError(f"{path} returned HTTP {resp.status}")
            self._rejected_at = None
            return resp

    def _ensure_open(self) -> None:
        """Raise if the DVR has been disconnected."""
        if self._closed:
            raise SpaceMonkeyError("The DVR has been disconnected")

    async def _renew_if_unchanged(self, seen_expiry: datetime | None) -> None:
        """Renew the certificate unless another request already has."""
        async with self._lock:
            self._ensure_open()
            if self.certificate_expiry == seen_expiry:
                await self._renew_certificate()

    async def _ensure_connected(self) -> None:
        """Connect if needed, and renew the certificate shortly before it expires."""
        async with self._lock:
            self._ensure_open()
            if self._ssl_context is None or self.certificate_expiry is None:
                await self._renew_certificate()
            elif self.certificate_expiry - datetime.now(UTC) < RENEW_MARGIN and (
                self._renew_failed_at is None
                or datetime.now(UTC) - self._renew_failed_at >= RENEW_RETRY_INTERVAL
                or self.certificate_expiry <= datetime.now(UTC)
            ):
                try:
                    await self._renew_certificate()
                    self._renew_failed_at = None
                except SpaceMonkeyError as err:
                    if self.certificate_expiry <= datetime.now(UTC):
                        raise
                    self._renew_failed_at = datetime.now(UTC)
                    _LOGGER.debug("Unable to renew the DVR certificate yet: %s", err)
            if self.address is None:
                await self._locate()

    def _client_session(self) -> aiohttp.ClientSession:
        """Return the HTTP session, creating one if there is none or it was closed."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    @_dvr_errors
    async def _renew_certificate(self) -> None:
        """Sign in to Space Monkey and download a fresh client certificate."""
        session = self._client_session()
        code = await self._api.get_authorization_code(
            CLIENT_ID, REDIRECT_URI, realm=REALM
        )
        async with session.get(
            REDIRECT_URI,
            params={"code": code},
            headers={"x-vivint-adapter": "BasicAuth"},
        ) as resp:
            if resp.status != 200:
                raise SpaceMonkeyError(f"Space Monkey sign-in failed: {resp.status}")

        async with session.get(
            f"{ACCOUNTS_ENDPOINT}/v2/playback/certs",
            params={"dvr_service_id": self._dvr_service_id},
        ) as resp:
            if resp.status != 200:
                raise SpaceMonkeyError(f"Certificate request failed: {resp.status}")
            data = await _read_json(resp, "certificate")

        try:
            bundle = base64.b64decode(data["pkcs12_b64"])
            expiry = datetime.fromisoformat(data["expires_at"])
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=UTC)
            hardware_id = data["hw_id"]
        except (KeyError, TypeError, ValueError) as err:
            raise SpaceMonkeyError("Unexpected certificate response") from err

        self._ssl_context = await asyncio.get_running_loop().run_in_executor(
            None, _build_ssl_context, bundle
        )
        self.hardware_id = hardware_id
        self.certificate_expiry = expiry
        _LOGGER.debug("Renewed the DVR certificate, valid until %s", expiry)

    @_dvr_errors
    async def _locate(self) -> None:
        """Ask the Space Monkey directory where the DVR is on the local network."""
        if not self.hardware_id:
            raise SpaceMonkeyError("A certificate is needed before locating the DVR")
        async with self._client_session().get(
            f"{DIRECTORY_ENDPOINT}/directory/mm/entry/hardware/{self.hardware_id}",
            params={"service": "playback"},
            headers={"Accept": "application/json"},
        ) as resp:
            if resp.status != 200:
                raise SpaceMonkeyError(f"Directory lookup failed: {resp.status}")
            entry = await _read_json(resp, "directory")
            try:
                entry = entry["address"]
                # lan_dns carries its own ":port" suffix.
                self.address = DvrAddress(
                    host=entry["lan_dns"].rsplit(":", 1)[0],
                    port=entry["local_port"],
                    local_ip=entry["local_ip"],
                )
            except (AttributeError, KeyError, TypeError, ValueError) as err:
                raise SpaceMonkeyError("Unexpected directory response") from err
        _LOGGER.debug("Located the DVR at %s", self.address.local_ip)

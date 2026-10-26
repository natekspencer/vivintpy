"""Module that implements access to the Space Monkey DVR attached to a Vivint system."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import re
import ssl
import tempfile
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from .exceptions import SpaceMonkeyError

if TYPE_CHECKING:
    from .api import VivintSkyApi

_LOGGER = logging.getLogger(__name__)

ACCOUNTS_ENDPOINT = "https://accounts.spacemonkey.com"
DIRECTORY_ENDPOINT = "https://directory.spacemonkey.com"
CLIENT_ID = "6af9ddae12d490ea76d9f30fa74e66f3"
REALM = "smas"
REDIRECT_URI = f"{ACCOUNTS_ENDPOINT}/users/vivint/authorized"
DVR_SERVICE_TYPE = "SPMO_DVR"

# Certificates last 24 hours; renew well before the DVR starts rejecting them.
RENEW_MARGIN = timedelta(minutes=30)

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
    for service in system_data.get("system", {}).get("srvs", []):
        if service.get("t") == DVR_SERVICE_TYPE:
            return cast("str | None", service.get("exid"))
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


def _from_microseconds(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1_000_000, tz=UTC)


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
    # The DVR issues 1024-bit client keys, which OpenSSL rejects at its default
    # security level. The relaxation only applies to connections made with this context.
    context.set_ciphers("DEFAULT:@SECLEVEL=0")
    # The device certificate is signed by Space Monkey's private CA, which is
    # delivered together with the client certificate.
    try:
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
        self.hardware_id: str | None = None
        self.certificate_expiry: datetime | None = None
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
            await self._renew_certificate()
            await self._locate()

    async def disconnect(self) -> None:
        """Close the session if it was created by this object."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._ssl_context = None

    async def get_status(self) -> dict[str, Any]:
        """Return the DVR's status, which includes its cameras."""
        async with await self.get("/web/v1/status") as resp:
            return cast("dict[str, Any]", await resp.json())

    async def get_recordings(self, camera_id: int) -> list[DvrRecording]:
        """Return the recorded ranges stored for a camera, oldest first."""
        async with await self.get("/recordings", camera=f"Video-{camera_id}") as resp:
            data = await resp.json()
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
                    start=_from_microseconds(item["StartTime"]),
                    end=_from_microseconds(item["EndTime"]),
                )
                for item in ranges
            ]
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as err:
            raise SpaceMonkeyError("Unexpected recordings response") from err

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
            async for chunk in resp.content.iter_chunked(1 << 16):
                yield chunk

    async def get(self, path: str, **params: str) -> aiohttp.ClientResponse:
        """
        Make a GET request to the DVR; the caller must release the response.

        Renews the certificate when it is about to expire and looks the DVR up again
        if it cannot be reached.
        """
        await self._ensure_connected()
        assert self._session
        for attempt in (1, 2):
            assert self.address
            url = f"https://{self.address.host}:{self.address.port}{path}"
            try:
                resp = await self._session.get(
                    url, params=params or None, ssl=self._ssl_context
                )
            except aiohttp.ClientConnectorError as err:
                if attempt == 2:
                    raise SpaceMonkeyError(f"Unable to reach the DVR: {err}") from err
                async with self._lock:
                    await self._locate()
                continue
            except aiohttp.ClientError as err:
                raise SpaceMonkeyError(f"DVR request failed: {err}") from err

            if resp.status == 401 and attempt == 1:
                resp.release()
                async with self._lock:
                    await self._renew_certificate()
                continue
            if resp.status != 200:
                resp.release()
                raise SpaceMonkeyError(f"{path} returned HTTP {resp.status}")
            return resp
        raise SpaceMonkeyError("Unable to complete the DVR request")

    async def _ensure_connected(self) -> None:
        async with self._lock:
            if not self.connected:
                await self._renew_certificate()
                await self._locate()
            elif (
                self.certificate_expiry is not None
                and self.certificate_expiry - datetime.now(UTC) < RENEW_MARGIN
            ):
                await self._renew_certificate()

    def _client_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

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
            data = await resp.json()

        try:
            bundle = base64.b64decode(data["pkcs12_b64"])
            expiry = datetime.fromisoformat(data["expires_at"])
            hardware_id = data["hw_id"]
        except (KeyError, ValueError) as err:
            raise SpaceMonkeyError("Unexpected certificate response") from err

        self._ssl_context = await asyncio.get_running_loop().run_in_executor(
            None, _build_ssl_context, bundle
        )
        self.hardware_id = hardware_id
        self.certificate_expiry = expiry
        _LOGGER.debug("Renewed the DVR certificate, valid until %s", expiry)

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
            try:
                entry = (await resp.json())["address"]
                # lan_dns carries its own ":port" suffix.
                self.address = DvrAddress(
                    host=entry["lan_dns"].rsplit(":", 1)[0],
                    port=entry["local_port"],
                    local_ip=entry["local_ip"],
                )
            except (KeyError, ValueError) as err:
                raise SpaceMonkeyError("Unexpected directory response") from err
        _LOGGER.debug("Located the DVR at %s", self.address.local_ip)

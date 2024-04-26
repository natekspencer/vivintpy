"""Module that implements the VivintSkyApi class."""

from __future__ import annotations

import json
import logging
import ssl
from collections.abc import Callable
from http.cookies import Morsel, SimpleCookie
from typing import Any, cast

import aiohttp
import certifi
import grpc
from aiohttp import ClientResponseError
from aiohttp.client import _RequestContextManager
from google.protobuf.message import Message  # type: ignore

from .const import (
    AuthenticationResponse,
    MfaVerificationResponse,
    SwitchAttribute,
    VivintDeviceAttribute,
)
from .enums import ArmedState, GarageDoorState, ZoneBypass
from .exceptions import (
    VivintSkyApiAuthenticationError,
    VivintSkyApiError,
    VivintSkyApiMfaRequiredError,
)
from .proto import beam_pb2, beam_pb2_grpc

_LOGGER = logging.getLogger(__name__)

API_ENDPOINT = "https://www.vivintsky.com/api"
GRPC_ENDPOINT = "grpc.vivintsky.com:50051"
MFA_ENDPOINT = (
    "https://www.vivintsky.com/platform-user-api/v0/platformusers/2fa/validate"
)


class VivintSkyApi:
    """Class to communicate with the VivintSky API."""

    def __init__(
        self,
        username: str,
        password: str,
        persist_session: bool = False,
        client_session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the VivintSky API."""
        self.__username = username
        self.__password = password
        self.__persist_session = persist_session
        self.__client_session = client_session or self.__get_new_client_session()
        self.__has_custom_client_session = client_session is not None
        self.__mfa_pending = False

    def _get_session_cookie(self) -> Morsel | None:
        """Get the session cookie."""
        cookie = self.__client_session.cookie_jar.filter_cookies(API_ENDPOINT)
        return cast(SimpleCookie, cookie).get("s")

    def is_session_valid(self) -> bool:
        """Return the state of the current session."""
        return self._get_session_cookie() is not None

    async def connect(self) -> dict:
        """Connect to VivintSky Cloud Service."""
        if self.__has_custom_client_session and self.is_session_valid():
            authuser_data = await self.get_authuser_data()
        else:
            authuser_data = await self.__get_vivintsky_session(
                self.__username, self.__password, self.__persist_session
            )
        if not authuser_data:
            raise VivintSkyApiAuthenticationError("Unable to login to Vivint")
        return authuser_data

    async def disconnect(self) -> None:
        """Disconnect from VivintSky Cloud Service."""
        if not self.__has_custom_client_session:
            await self.__client_session.close()

    async def verify_mfa(self, code: str) -> None:
        """Verify multi-factor authentication code."""
        resp = await self.__post(MFA_ENDPOINT, data=json.dumps({"code": code}))
        if resp is not None:
            self.__mfa_pending = False

    async def get_authuser_data(self) -> dict:
        """
        Get the authuser data.

        Poll the Vivint authuser API endpoint resource to gather user-related data including enumeration of the systems
        that user has access to.
        """
        resp = await self.__get("authuser")
        if not resp:
            raise VivintSkyApiAuthenticationError("Missing auth user data")
        return resp

    async def get_panel_credentials(self, panel_id: int) -> dict:
        """Get the panel credentials."""
        resp = await self.__get(f"panel-login/{panel_id}")
        if not resp:
            raise VivintSkyApiAuthenticationError(
                "Unable to retrieve panel credentials."
            )
        return resp

    async def get_system_data(self, panel_id: int) -> dict:
        """Get the raw data for a system."""
        resp = await self.__get(
            f"systems/{panel_id}",
            headers={"Accept-Encoding": "application/json"},
            params={"includerules": "false"},
        )
        if not resp:
            raise VivintSkyApiError("Unable to retrieve system data")
        return resp

    async def get_system_update(self, panel_id: int) -> dict:
        """Get panel software update details."""
        resp = await self.__get(
            f"systems/{panel_id}/system-update",
            headers={"Accept-Encoding": "application/json"},
        )
        if not resp:
            raise VivintSkyApiError("Unable to retrieve system update")
        return resp

    async def update_panel_software(self, panel_id: int) -> None:
        """Request a panel software update."""
        if not await self.__post(f"systems/{panel_id}/system-update"):
            raise VivintSkyApiError("Unable to update panel software")

    async def reboot_camera(
        self, panel_id: int, device_id: int, device_type: str
    ) -> None:
        """Reboot a camera."""

        async def _callback(
            stub: beam_pb2_grpc.BeamStub, metadata: list[tuple[str, str]]
        ) -> Message:
            return await stub.RebootCamera(
                beam_pb2.RebootCameraRequest(  # pylint: disable=no-member
                    panel_id=panel_id, device_id=device_id, device_type=device_type
                ),
                metadata=metadata,
            )

        await self._send_grpc(_callback)

    async def reboot_panel(self, panel_id: int) -> None:
        """Reboot a panel."""
        if not await self.__post(f"systems/{panel_id}/reboot-panel"):
            raise VivintSkyApiError("Unable to reboot panel")

    async def get_device_data(self, panel_id: int, device_id: int) -> dict:
        """Get the raw data for a device."""
        resp = await self.__get(
            f"system/{panel_id}/device/{device_id}",
            headers={"Accept-Encoding": "application/json"},
        )
        if not resp:
            raise VivintSkyApiError("Unable to retrieve device data")
        return resp

    async def set_alarm_state(
        self, panel_id: int, partition_id: int, state: int
    ) -> None:
        """Set the alarm state."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/armedstates",
            headers={"Content-Type": "application/json;charset=UTF-8"},
            data=json.dumps(
                {
                    "system": panel_id,
                    "partitionId": partition_id,
                    "armState": state,
                    "forceArm": False,
                }
            ),
        )
        if resp is None:
            _LOGGER.error(
                "Failed to set state to %s for panel %s",
                ArmedState(state).name,
                panel_id,
            )
            raise VivintSkyApiError("Failed to set alarm state")

    async def trigger_alarm(self, panel_id: int, partition_id: int) -> None:
        """Trigger an alarm."""
        if not await self.__post(f"{panel_id}/{partition_id}/alarm"):
            _LOGGER.error("Failed to trigger alarm for panel %s", panel_id)
            raise VivintSkyApiError("Failed to trigger alarm")

    async def set_camera_as_doorbell_chime_extender(
        self, panel_id: int, device_id: int, state: bool
    ) -> None:
        """Set the camera to be used as a doorbell chime extender."""

        async def _callback(
            stub: beam_pb2_grpc.BeamStub, metadata: list[tuple[str, str]]
        ) -> Message:
            return await stub.SetUseAsDoorbellChimeExtender(
                beam_pb2.SetUseAsDoorbellChimeExtenderRequest(  # pylint: disable=no-member
                    panel_id=panel_id,
                    device_id=device_id,
                    use_as_doorbell_chime_extender=state,
                ),
                metadata=metadata,
            )

        await self._send_grpc(_callback)

    async def set_camera_privacy_mode(
        self, panel_id: int, device_id: int, state: bool
    ) -> None:
        """Set the camera privacy mode."""

        async def _callback(
            stub: beam_pb2_grpc.BeamStub, metadata: list[tuple[str, str]]
        ) -> Message:
            return await stub.SetCameraPrivacyMode(
                beam_pb2.SetCameraPrivacyModeRequest(  # pylint: disable=no-member
                    panel_id=panel_id, device_id=device_id, privacy_mode=state
                ),
                metadata=metadata,
            )

        await self._send_grpc(_callback)

    async def set_camera_deter_mode(
        self, panel_id: int, device_id: int, state: bool
    ) -> None:
        """Set the camera deter mode."""

        async def _callback(
            stub: beam_pb2_grpc.BeamStub, metadata: list[tuple[str, str]]
        ) -> Message:
            return await stub.SetDeterOverride(
                beam_pb2.SetDeterOverrideRequest(  # pylint: disable=no-member
                    panel_id=panel_id, device_id=device_id, enabled=state
                ),
                metadata=metadata,
            )

        await self._send_grpc(_callback)

    async def set_garage_door_state(
        self, panel_id: int, partition_id: int, device_id: int, state: int
    ) -> None:
        """Open/Close garage door."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/door/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(
                {
                    VivintDeviceAttribute.STATE: state,
                    VivintDeviceAttribute.ID: device_id,
                }
            ),
        )
        if resp is None:
            _LOGGER.debug(
                "Failed to set state to %s for garage door %s @ %s:%s",
                GarageDoorState(state).name,
                device_id,
                panel_id,
                partition_id,
            )
            raise VivintSkyApiError("Failed to set garage door state")

    async def set_lock_state(
        self, panel_id: int, partition_id: int, device_id: int, locked: bool
    ) -> None:
        """Lock/Unlock door lock."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/locks/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(
                {
                    VivintDeviceAttribute.STATE: locked,
                    VivintDeviceAttribute.ID: device_id,
                }
            ),
        )
        if resp is None:
            _LOGGER.debug(
                "Failed to set state to %s for lock %s @ %s:%s",
                locked,
                device_id,
                panel_id,
                partition_id,
            )
            raise VivintSkyApiError("Failed to set lock state")

    async def set_sensor_state(
        self, panel_id: int, partition_id: int, device_id: int, bypass: bool
    ) -> None:
        """Bypass/unbypass a sensor."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/sensors/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(
                {
                    VivintDeviceAttribute.BYPASSED: ZoneBypass.MANUALLY_BYPASSED
                    if bypass
                    else ZoneBypass.UNBYPASSED,
                    VivintDeviceAttribute.ID: device_id,
                }
            ),
        )
        if resp is None:
            _LOGGER.debug(
                "Failed to set state to %s for sensor %s @ %s:%s",
                "bypassed" if bypass else "unbypassed",
                device_id,
                panel_id,
                partition_id,
            )
            raise VivintSkyApiError("Failed to set sensor state")

    async def set_switch_state(
        self,
        panel_id: int,
        partition_id: int,
        device_id: int,
        on: bool | None = None,  # pylint: disable=invalid-name
        level: int | None = None,
    ) -> None:
        """Set switch state."""
        # validate input
        if on is None and level is None:
            raise VivintSkyApiError('Either "on" or "level" must be provided.')
        if level and (0 > level or level > 100):
            raise VivintSkyApiError('The value for "level" must be between 0 and 100.')

        data: dict = {SwitchAttribute.ID: device_id}
        if level is None:
            data[SwitchAttribute.STATE] = on
        else:
            data[SwitchAttribute.VALUE] = level

        resp = await self.__put(
            f"{panel_id}/{partition_id}/switches/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(data),
        )
        if resp is None:
            _LOGGER.debug(
                "Failed to set %s to %s for switch %s @ %s:%s",
                "on" if level is None else "level",
                on if level is None else level,
                device_id,
                panel_id,
                partition_id,
            )
            raise VivintSkyApiError("Failed to set switch state")

    async def set_thermostat_state(
        self, panel_id: int, partition_id: int, device_id: int, **kwargs: Any
    ) -> None:
        """Set thermostat state."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/thermostats/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(kwargs),
        )
        if resp is None:
            _LOGGER.debug(
                "Failed to set state to %s for thermostat %s @ %s:%s",
                kwargs,
                device_id,
                panel_id,
                partition_id,
            )
            raise VivintSkyApiError("Failed to set thermostat state")

    async def request_camera_thumbnail(
        self, panel_id: int, partition_id: int, device_id: int
    ) -> None:
        """Request the camera thumbnail."""
        try:
            await self.__get(
                f"{panel_id}/{partition_id}/{device_id}/request-camera-thumbnail",
            )
        except ClientResponseError as resp:
            if resp.status < 200 or resp.status > 299:
                _LOGGER.error(
                    "Failed to request thumbnail for camera %s @ %s:%s with status code %s",
                    device_id,
                    panel_id,
                    partition_id,
                    resp.status,
                )

    async def get_camera_thumbnail_url(
        self, panel_id: int, partition_id: int, device_id: int, thumbnail_timestamp: int
    ) -> str | None:
        """Get the camera thumbnail url."""
        try:
            resp = await self.__get(
                f"{panel_id}/{partition_id}/{device_id}/camera-thumbnail",
                params={"time": thumbnail_timestamp},
                allow_redirects=False,
            )
            assert resp
            return resp.get("location")
        except ClientResponseError as resp:
            if resp.status != 302:
                _LOGGER.debug(
                    "Failed to get thumbnail for camera %s @ %s:%s with status code %s",
                    device_id,
                    panel_id,
                    partition_id,
                    resp.status,
                )
            return None

    def __get_new_client_session(self) -> aiohttp.ClientSession:
        """Create a new aiohttp.ClientSession object."""
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=certifi.where()
        )
        connector = aiohttp.TCPConnector(enable_cleanup_closed=True, ssl=ssl_context)

        return aiohttp.ClientSession(connector=connector)

    async def __get_vivintsky_session(
        self, username: str, password: str, persist_session: bool = False
    ) -> dict:
        """Login into the Vivint Sky platform with the given username, password and, optionally, persist the session.

        Returns auth user data if successful.
        """
        resp = await self.__post(
            "login",
            data=json.dumps(
                {
                    "username": username,
                    "password": password,
                    "persist_session": persist_session,
                }
            ),
        )
        assert resp
        return resp

    async def __get(
        self,
        path: str,
        headers: dict | None = None,
        params: dict | None = None,
        allow_redirects: bool | None = None,
    ) -> dict | None:
        """Perform a get request."""
        return await self.__call(
            self.__client_session.get,
            path,
            headers=headers,
            params=params,
            allow_redirects=allow_redirects,
        )

    async def __post(self, path: str, data: str | None = None) -> dict | None:
        """Perform a post request."""
        return await self.__call(self.__client_session.post, path, data=data)

    async def __put(
        self, path: str, headers: dict | None = None, data: str | None = None
    ) -> dict | None:
        """Perform a put request."""
        return await self.__call(
            self.__client_session.put, path, headers=headers, data=data
        )

    async def __call(
        self,
        method: Callable[..., _RequestContextManager],
        path: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: str | None = None,
        allow_redirects: bool | None = None,
    ) -> dict | None:
        """Perform a request with supplied parameters and reauthenticate if necessary."""
        if path != "login" and not self.is_session_valid():
            await self.connect()

        if self.__client_session.closed:
            raise VivintSkyApiError("The client session has been closed")

        is_mfa_request = path == MFA_ENDPOINT

        if self.__mfa_pending and not is_mfa_request:
            raise VivintSkyApiMfaRequiredError(AuthenticationResponse.MFA_REQUIRED)

        resp = await method(
            path if is_mfa_request else f"{API_ENDPOINT}/{path}",
            headers=headers,
            params=params,
            data=data,
            allow_redirects=allow_redirects,
        )
        async with resp:
            if resp.content_type != "application/json":
                resp_data = {AuthenticationResponse.MESSAGE: await resp.text()}
            else:
                resp_data = await resp.json(encoding="utf-8")
            if resp.status == 200:
                return resp_data
            if resp.status == 302:
                return {"location": resp.headers.get("Location")}
            if resp.status in (400, 401, 403):
                message = (
                    resp_data.get(MfaVerificationResponse.MESSAGE)
                    if is_mfa_request
                    else resp_data.get(AuthenticationResponse.MESSAGE)
                )
                if message == AuthenticationResponse.MFA_REQUIRED or is_mfa_request:
                    self.__mfa_pending = True
                    raise VivintSkyApiMfaRequiredError(message)
                if resp.status == 400:
                    raise VivintSkyApiError(message)
                raise VivintSkyApiAuthenticationError(message)
            resp.raise_for_status()
            return None

    async def _send_grpc(
        self,
        callback: Callable[[beam_pb2_grpc.BeamStub, list[tuple[str, str]]], Message],
    ) -> None:
        """Send gRPC."""
        creds = grpc.ssl_channel_credentials()
        assert (cookie := self._get_session_cookie())

        async with grpc.aio.secure_channel(GRPC_ENDPOINT, credentials=creds) as channel:
            stub: beam_pb2_grpc.BeamStub = beam_pb2_grpc.BeamStub(channel)  # type: ignore
            response = await callback(stub, [("session", cookie.value)])
            _LOGGER.debug("Response received: %s", str(response))

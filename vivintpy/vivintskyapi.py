"""Module that implements the VivintSkyApi class."""
import json
import logging
import ssl
from datetime import datetime
from types import MethodType
from typing import Any, Dict, Optional

import aiohttp
import certifi
from aiohttp.client_reqrep import ClientResponse

from .const import SwitchAttribute, VivintDeviceAttribute, WirelessSensorAttribute
from .enums import ArmedState, GarageDoorState, ZoneBypass
from .exceptions import VivintSkyApiAuthenticationError, VivintSkyApiError

_LOGGER = logging.getLogger(__name__)

VIVINT_API_ENDPOINT = "https://www.vivintsky.com/api"


class VivintSkyApi:
    """Class to communicate with the VivintSky API."""

    def __init__(
        self,
        username: str,
        password: str,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__username = username
        self.__password = password
        self.__client_session = client_session or self.__get_new_client_session()
        self.__has_custom_client_session = client_session is not None

    def is_session_valid(self) -> dict:
        """Return the state of the current session."""
        cookie = self.__client_session.cookie_jar._cookies["www.vivintsky.com"].get("s")
        if not cookie:
            return False
        cookie_expiration = datetime.strptime(
            cookie.get("expires"), "%a, %d %b %Y %H:%M:%S %Z"
        )
        return True if cookie_expiration > datetime.utcnow() else False

    async def connect(self) -> dict:
        """Connect to VivintSky Cloud Service."""
        authuser_data = await self.__get_vivintsky_session(
            self.__username, self.__password
        )
        if not authuser_data:
            raise VivintSkyApiAuthenticationError("Unable to login to Vivint.")
        return authuser_data

    async def disconnect(self) -> None:
        """Disconnect from VivintSky Cloud Service."""
        if not self.__has_custom_client_session:
            await self.__client_session.close()

    async def get_authuser_data(self) -> dict:
        """
        Get the authuser data

        Poll the Vivint authuser API endpoint resource to gather user-related data including enumeration of the systems
        that user has access to.
        """
        resp = await self.__get("authuser")
        async with resp:
            if resp.status == 200:
                return await resp.json(encoding="utf-8")
            else:
                raise VivintSkyApiAuthenticationError("Missing auth user data.")

    async def get_panel_credentials(self, panel_id: int) -> dict:
        """Get the panel credentials."""
        resp = await self.__get(f"panel-login/{panel_id}")
        async with resp:
            if resp.status == 200:
                return await resp.json(encoding="utf-8")
            else:
                raise VivintSkyApiAuthenticationError(
                    "Unable to retrieve panel credentials."
                )

    async def get_system_data(self, panel_id: int) -> dict:
        """Gets the raw data for a system."""
        resp = await self.__get(
            f"systems/{panel_id}",
            headers={"Accept-Encoding": "application/json"},
            params={"includerules": "false"},
        )
        async with resp:
            if resp.status == 200:
                return await resp.json(encoding="utf-8")
            else:
                raise VivintSkyApiError("Unable to retrieve system data.")

    async def get_device_data(self, panel_id: int, device_id: int) -> dict:
        """Gets the raw data for a device."""
        resp = await self.__get(
            f"system/{panel_id}/device/{device_id}",
            headers={"Accept-Encoding": "application/json"},
        )
        async with resp:
            if resp.status == 200:
                return await resp.json(encoding="utf-8")
            else:
                raise VivintSkyApiError("Unable to retrieve device data.")

    async def set_alarm_state(
        self, panel_id: int, partition_id: int, state: bool
    ) -> aiohttp.ClientResponse:
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
            ).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                resp_body = await resp.text()
                _LOGGER.error(
                    f"failed to set state {ArmedState.name(state)}. Code: {resp.status}, body: {resp_body},"
                    f"request url: {resp.request_info}"
                )
                raise VivintSkyApiError(
                    f"failed to set alarm status {ArmedState.name(state)} for panel {self.id}"
                )

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
            ).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                _LOGGER.debug(
                    "Failed to set state to %s for garage door: %s @ %s:%s",
                    GarageDoorState.name(state),
                    device_id,
                    panel_id,
                    partition_id,
                )
                raise VivintSkyApiError(f"Failed to update garage door state")

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
            ).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                _LOGGER.debug(
                    "Failed to set locked status to %s for lock: %s @ %s:%s",
                    locked,
                    device_id,
                    panel_id,
                    partition_id,
                )
                raise VivintSkyApiError(f"Failed to update lock status")

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
                    WirelessSensorAttribute.BYPASSED: ZoneBypass.MANUALLY_BYPASSED
                    if bypass
                    else ZoneBypass.UNBYPASSED,
                    VivintDeviceAttribute.ID: device_id,
                }
            ).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                _LOGGER.debug(
                    "Failed to set bypass status to %s for sensor: %s @ %s:%s",
                    bypass,
                    device_id,
                    panel_id,
                    partition_id,
                )
                raise VivintSkyApiError(f"Failed to update sensor status")

    async def set_switch_state(
        self,
        panel_id: int,
        partition_id: int,
        device_id: int,
        on: Optional[bool] = None,
        level: Optional[int] = None,
    ) -> None:
        """Set switch state."""
        # validate input
        if on is None and level is None:
            raise VivintSkyApiError('Either "on" or "level" must be provided.')
        elif level and (0 > level or level > 100):
            raise VivintSkyApiError('The value for "level" must be between 0 and 100.')

        resp = await self.__put(
            f"{panel_id}/{partition_id}/switches/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(
                {
                    SwitchAttribute.ID: device_id,
                    **(
                        {SwitchAttribute.STATE: on}
                        if level is None
                        else {SwitchAttribute.VALUE: level}
                    ),
                }
            ).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                [attribute, value] = ["on", on] if level is None else ["level", level]
                _LOGGER.debug(
                    "Failed to set %s to %s for switch: %s @ %s:%s.",
                    attribute,
                    value,
                    device_id,
                    panel_id,
                    partition_id,
                )
                raise VivintSkyApiError("Failed to update switch state.")

    async def set_thermostat_state(
        self, panel_id: int, partition_id: int, device_id: int, **kwargs
    ) -> None:
        """Set thermostat state."""
        resp = await self.__put(
            f"{panel_id}/{partition_id}/thermostats/{device_id}",
            headers={
                "Content-Type": "application/json;charset=utf-8",
            },
            data=json.dumps(kwargs).encode("utf-8"),
        )
        async with resp:
            if resp.status != 200:
                _LOGGER.debug(
                    "Failed to set state to %s for thermostat: %s @ %s:%s",
                    kwargs,
                    device_id,
                    panel_id,
                    partition_id,
                )
                raise VivintSkyApiError(f"Failed to update thermostat state")

    async def request_camera_thumbnail(
        self, panel_id: int, partition_id: int, device_id: int
    ) -> None:
        resp = await self.__get(
            f"{panel_id}/{partition_id}/{device_id}/request-camera-thumbnail",
        )
        async with resp:
            if resp.status < 200 or resp.status > 299:
                _LOGGER.debug(
                    "Failed to request thumbnail for camera id %s with error code: %s",
                    self.id,
                    resp.status,
                )

    async def get_camera_thumbnail_url(
        self,
        panel_id: int,
        partition_id: int,
        device_id: int,
        thumbnail_timestamp: datetime,
    ) -> str:
        resp = await self.__get(
            f"{panel_id}/{partition_id}/{device_id}/camera-thumbnail",
            params={"time": thumbnail_timestamp},
            allow_redirects=False,
        )
        async with resp:
            if resp.status != 302:
                _LOGGER.debug(
                    "Failed to get thumbnail for camera id %s with status code: %s",
                    self.id,
                    resp.status,
                )
                return

            return resp.headers.get("Location")

    def __get_new_client_session(self) -> aiohttp.ClientSession:
        """Create a new aiohttp.ClientSession object."""
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=certifi.where()
        )
        connector = aiohttp.TCPConnector(enable_cleanup_closed=True, ssl=ssl_context)

        return aiohttp.ClientSession(connector=connector)

    async def __get_vivintsky_session(self, username: str, password: str) -> dict:
        """Login into the Vivint Sky platform with the given username and password.

        Returns auth user data if successful.
        """
        resp = await self.__post(
            "login",
            data=json.dumps({"username": username, "password": password}).encode(
                "utf-8"
            ),
        )
        async with resp:
            data = await resp.json(encoding="utf-8")
            if resp.status == 200:
                return data
            elif resp.status == 401:
                raise VivintSkyApiAuthenticationError(data["msg"])
            else:
                resp.raise_for_status()
                return None

    async def __get(
        self,
        path: str,
        headers: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        allow_redirects: bool = None,
    ) -> ClientResponse:
        """Perform a get request."""
        return await self.__call(
            self.__client_session.get,
            path,
            headers=headers,
            params=params,
            allow_redirects=allow_redirects,
        )

    async def __post(
        self,
        path: str,
        data: bytes = None,
    ) -> ClientResponse:
        """Perform a post request."""
        return await self.__call(self.__client_session.post, path, data=data)

    async def __put(
        self,
        path: str,
        headers: Dict[str, Any] = None,
        data: bytes = None,
    ) -> ClientResponse:
        """Perform a put request."""
        return await self.__call(
            self.__client_session.put, path, headers=headers, data=data
        )

    async def __call(
        self,
        method: MethodType,
        path: str,
        headers: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        data: bytes = None,
        allow_redirects: bool = None,
    ) -> ClientResponse:
        """Perform a request with supplied parameters and reauthenticate if necessary."""
        if path != "login" and not self.is_session_valid():
            await self.connect()

        if self.__client_session.closed:
            raise VivintSkyApiError("The client session has been closed")

        return await method(
            f"{VIVINT_API_ENDPOINT}/{path}",
            headers=headers,
            params=params,
            data=data,
            allow_redirects=allow_redirects,
        )

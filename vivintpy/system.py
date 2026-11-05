"""Module that implements the System class."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from .api import VivintSkyApi
from .const import PubNubMessageAttribute
from .const import SystemAttribute as Attribute
from .devices.alarm_panel import DEVICE_DELETED, DEVICE_DISCOVERED, AlarmPanel
from .devices.climate_thermostat import ClimateThermostat
from .devices.thermostat import Thermostat
from .entity import Entity
from .exceptions import VivintSkyApiError
from .proto import climate_pb2
from .user import User
from .utils import first_or_none

_LOGGER = logging.getLogger(__name__)

CLIMATE_RETRY_MIN = 5
CLIMATE_RETRY_MAX = 300
CLIMATE_REFRESH_DELAY = 2


class System(Entity):
    """Describe a vivint system."""

    def __init__(self, data: dict, api: VivintSkyApi, *, name: str, is_admin: bool):
        """Initialize a system."""
        super().__init__(data)
        self._api = api
        self._name = name
        self._is_admin = is_admin
        self.alarm_panels: list[AlarmPanel] = [
            AlarmPanel(panel_data, self)
            for panel_data in self.data[Attribute.SYSTEM][Attribute.PARTITION]
        ]
        self.users = [
            User(user_data, self)
            for user_data in self.data[Attribute.SYSTEM][Attribute.USERS]
        ]
        self._climate_task: asyncio.Task | None = None
        self._climate_refresh_task: asyncio.Task | None = None
        self._climate_stream_connected = False

    @property
    def api(self) -> VivintSkyApi:
        """Return the API."""
        return self._api

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """System's id."""
        return int(self.data[Attribute.SYSTEM][Attribute.PANEL_ID])

    @property
    def is_admin(self) -> bool:
        """Return True if the user is an admin for this system."""
        return self._is_admin

    @property
    def name(self) -> str:
        """System's name."""
        return self._name

    async def refresh(self) -> None:
        """Reload a system's data from the VivintSky API."""
        system_data = await self.api.get_system_data(self.id)

        for panel_data in system_data[Attribute.SYSTEM][Attribute.PARTITION]:
            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel, panel_data=panel_data: (  # type: ignore
                    panel.id == panel_data[Attribute.PANEL_ID]
                    and panel.partition_id == panel_data[Attribute.PARTITION_ID]
                ),
            )
            if alarm_panel:
                alarm_panel.refresh(panel_data)
            else:
                self.alarm_panels.append(AlarmPanel(panel_data, self))

        await self.load_climate_devices()

    @property
    def climate_updates_running(self) -> bool:
        """Return `True` if thermostat updates are being received in real time."""
        return (
            self._climate_task is not None
            and not self._climate_task.done()
            and self._climate_stream_connected
        )

    async def load_climate_devices(self) -> None:
        """Load the thermostats managed by the climate service."""
        try:
            devices = await self.api.get_climate_devices(self.id)
        except VivintSkyApiError as err:
            _LOGGER.debug(
                "Unable to load climate devices for system %s: %s", self.id, err
            )
            return
        self.update_climate_devices(devices, snapshot=True)

    def start_climate_updates(self) -> None:
        """Receive thermostat updates in real time."""
        if self._climate_task is None or self._climate_task.done():
            self._climate_task = asyncio.create_task(self._stream_climate_devices())

    async def stop_climate_updates(self) -> None:
        """Stop receiving thermostat updates."""
        for task in (self._climate_task, self._climate_refresh_task):
            if task:
                task.cancel()
        await asyncio.gather(
            *(t for t in (self._climate_task, self._climate_refresh_task) if t),
            return_exceptions=True,
        )
        self._climate_task = self._climate_refresh_task = None

    def request_climate_refresh(self) -> None:
        """Reload the thermostats soon, unless real time updates are running."""
        if self.climate_updates_running:
            return
        if self._climate_refresh_task is None or self._climate_refresh_task.done():
            self._climate_refresh_task = asyncio.create_task(
                self._refresh_climate_devices_later()
            )

    async def _refresh_climate_devices_later(self) -> None:
        """Reload the thermostats after giving the service time to apply a change."""
        await asyncio.sleep(CLIMATE_REFRESH_DELAY)
        await self.load_climate_devices()

    async def _stream_climate_devices(self) -> None:
        """Apply thermostat updates from the climate service, reconnecting on failure."""
        delay = CLIMATE_RETRY_MIN
        while True:
            try:
                async for response in self.api.stream_climate_devices(self.id):
                    delay = CLIMATE_RETRY_MIN
                    self._climate_stream_connected = True
                    self.update_climate_devices(
                        response.climate_devices, response.deleted_device_ids
                    )
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Climate updates for system %s stopped: %s", self.id, err)
            else:
                _LOGGER.debug("Climate updates for system %s ended", self.id)
            self._climate_stream_connected = False
            await asyncio.sleep(delay)
            delay = min(delay * 2, CLIMATE_RETRY_MAX)

    def update_climate_devices(
        self,
        devices: Iterable[climate_pb2.ClimateDevice],
        deleted_ids: Iterable[str] = (),
        *,
        snapshot: bool = False,
    ) -> None:
        """Create, update and remove climate thermostats on the system's panel.

        With `snapshot`, `devices` is the complete list and any other known thermostat
        is removed.
        """
        if not self.alarm_panels:
            return
        panel = self.alarm_panels[0]
        known = {
            device.id: device
            for panel_ in self.alarm_panels
            for device in panel_.devices
            if isinstance(device, ClimateThermostat)
        }
        legacy_ids = {
            str(device.id)
            for panel_ in self.alarm_panels
            for device in panel_.devices
            if isinstance(device, Thermostat)
            and not isinstance(device, ClimateThermostat)
        }
        devices = list(devices)
        removed_ids = set(deleted_ids)
        if snapshot:
            removed_ids |= known.keys() - {data.id for data in devices}

        for data in devices:
            if existing := known.get(data.id):
                existing.update_device(data)
            elif _legacy_device_id(data.id) not in legacy_ids:
                device = ClimateThermostat(data, panel)
                panel.devices.append(device)
                panel.emit(DEVICE_DISCOVERED, {"device": device})

        for device_id in removed_ids:
            if removed := known.get(device_id):
                owner = removed.alarm_panel or panel
                owner.devices.remove(removed)
                owner.emit(DEVICE_DELETED, {"device": removed})

    def update_user_data(self, data: list[dict]) -> None:
        """Update user data."""
        for d in data:

            def _matches(user: User, _id: str = d["_id"]) -> bool:
                return user.id == _id

            user = first_or_none(self.users, _matches)
            if not user:
                _LOGGER.debug("User not found for system %s: %s", self.id, d)
                return
            user.handle_pubnub_message(d)

    def __update_changed_by(self, data: dict) -> None:
        """
        Update the alarm panels with what armed or disarmed the system.

        These events are sent for the system rather than a partition, so they go to
        the panels in the event's state. They can arrive before the panel's own state
        update, so they go to every panel if none match.
        """
        for key in (Attribute.SECURITY_ARMED, Attribute.SECURITY_DISARMED):
            if not isinstance(event := data.get(key), dict):
                continue
            state = event.get(Attribute.SECURITY_STATE)
            panels = [panel for panel in self.alarm_panels if panel.state == state]
            for panel in panels or self.alarm_panels:
                panel.update_changed_by(event.get(Attribute.SECURITY_NAME))

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message."""
        if (message_type := message[PubNubMessageAttribute.TYPE]) == "account_system":
            # this is a system message
            operation = message.get(PubNubMessageAttribute.OPERATION)
            data = message.get(PubNubMessageAttribute.DATA)

            if data and operation == "u":
                if Attribute.USERS in data:
                    self.update_user_data(data[Attribute.USERS])
                    del data[Attribute.USERS]
                self.update_data(data)
                self.__update_changed_by(data)

        elif message_type == "account_partition":
            # this is a message for one of the devices attached to this system
            partition_id = message.get(PubNubMessageAttribute.PARTITION_ID)
            if not partition_id:
                _LOGGER.debug(
                    "Ignoring account partition message (no partition id specified for system %s): %s",
                    self.id,
                    message,
                )
                return

            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel: (
                    panel.id == self.id and panel.partition_id == partition_id
                ),
            )

            if not alarm_panel:
                _LOGGER.debug(
                    "No alarm panel found for system %s, partition %s",
                    self.id,
                    partition_id,
                )
                return

            alarm_panel.handle_pubnub_message(message)
        elif message_type == "adaptive_home_settings":
            # Smart Comfort's home or away state, which nothing uses yet
            _LOGGER.debug(
                "Ignoring adaptive home settings for system %s: %s", self.id, message
            )
        else:
            _LOGGER.warning(
                "Unknown message received by system %s: %s", self.id, message
            )


def _legacy_device_id(urn: str) -> str | None:
    """Return the trailing numeric device id of a device URN, if it has one."""
    _, _, device_id = urn.rpartition(":")
    return device_id if device_id.isdigit() else None

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
        return self._climate_task is not None and not self._climate_task.done()

    async def load_climate_devices(self) -> None:
        """Load the thermostats managed by the climate service."""
        try:
            devices = await self.api.get_climate_devices(self.id)
        except VivintSkyApiError as err:
            _LOGGER.debug(
                "Unable to load climate devices for system %s: %s", self.id, err
            )
            return
        self.update_climate_devices(devices)

    def start_climate_updates(self) -> None:
        """Receive thermostat updates in real time."""
        if not self.climate_updates_running:
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
                self.load_climate_devices()
            )

    async def _stream_climate_devices(self) -> None:
        """Apply thermostat updates from the climate service, reconnecting on failure."""
        delay = CLIMATE_RETRY_MIN
        while True:
            try:
                async for response in self.api.stream_climate_devices(self.id):
                    delay = CLIMATE_RETRY_MIN
                    self.update_climate_devices(
                        response.climate_devices, response.deleted_device_ids
                    )
            except VivintSkyApiError as err:
                _LOGGER.debug("Climate updates for system %s stopped: %s", self.id, err)
            else:
                _LOGGER.debug("Climate updates for system %s ended", self.id)
            await asyncio.sleep(delay)
            delay = min(delay * 2, CLIMATE_RETRY_MAX)

    def update_climate_devices(
        self,
        devices: Iterable[climate_pb2.ClimateDevice],
        deleted_ids: Iterable[str] = (),
    ) -> None:
        """Create, update and remove climate thermostats on the system's panel."""
        if not self.alarm_panels:
            return
        panel = self.alarm_panels[0]
        known = {
            device.id: device
            for device in panel.devices
            if isinstance(device, ClimateThermostat)
        }
        legacy_ids = {
            device.id
            for device in panel.devices
            if isinstance(device, Thermostat)
            and not isinstance(device, ClimateThermostat)
        }

        for data in devices:
            if existing := known.get(data.id):
                existing.update_device(data)
            elif _legacy_device_id(data.id) not in legacy_ids:
                device = ClimateThermostat(data, panel)
                panel.devices.append(device)
                panel.emit(DEVICE_DISCOVERED, {"device": device})

        for device_id in deleted_ids:
            if removed := known.get(device_id):
                panel.devices.remove(removed)
                panel.emit(DEVICE_DELETED, {"device": removed})

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
        else:
            _LOGGER.warning(
                "Unknown message received by system %s: %s", self.id, message
            )


def _legacy_device_id(urn: str) -> int | None:
    """Return the numeric device id embedded in a panel device URN, if any."""
    prefix, _, device_id = urn.rpartition(":")
    return (
        int(device_id)
        if prefix.startswith("urn:vivint:panel:") and device_id.isdigit()
        else None
    )

"""Module that implements the AlarmPanel class."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Type

from ..const import AlarmPanelAttribute as Attribute
from ..const import PubNubMessageAttribute, PubNubOperatorAttribute, SystemAttribute
from ..enums import ArmedState, DeviceType
from ..exceptions import VivintSkyApiError
from ..utils import add_async_job, first_or_none
from ..vivintskyapi import VivintSkyApi
from . import VivintDevice, get_device_class

if TYPE_CHECKING:
    from ..system import System

_LOGGER = logging.getLogger(__name__)

DEVICE_DELETED = "device_deleted"
DEVICE_DISCOVERED = "device_discovered"


class AlarmPanel(VivintDevice):
    """Describe a Vivint alarm panel."""

    def __init__(self, data: dict, system: System):
        """Initialize an alarm panel."""
        self.system = system
        super().__init__(data)
        self.devices: list[VivintDevice] = []
        self.unregistered_devices: dict[int, tuple] = {}

        self.__parse_data(data=data, init=True)

        # store a reference to the physical panel device
        self.__panel_credentials = None
        self.__panel = first_or_none(
            self.devices,
            lambda device: DeviceType(device.data.get(Attribute.TYPE))
            == DeviceType.TOUCH_PANEL,
        )

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Instance of VivitSkyApi."""
        return self.system.vivintskyapi

    @property
    def id(self) -> int:
        """Panel's id."""
        return self.data[Attribute.PANEL_ID]

    @property
    def name(self) -> str:
        """Panel's name."""
        return self.system.name

    @property
    def manufacturer(self):
        """Return Vivint as the manufacturer of this panel."""
        return "Vivint"

    @property
    def model(self):
        """Return the model of the physical panel."""
        return (
            "Sky Control"
            if self.__panel and self.__panel.data["pant"] == 1
            else "Smart Hub"
        )

    @property
    def software_version(self) -> str:
        """Return the software version of the panel."""
        return self.__panel.software_version if self.__panel else None

    @property
    def partition_id(self) -> int:
        """Panel's partition id."""
        return self.data[Attribute.PARTITION_ID]

    @property
    def is_disarmed(self) -> bool:
        """Return True if alarm is disarmed."""
        return self.get_armed_state() == ArmedState.DISARMED

    @property
    def is_armed_away(self) -> bool:
        """Return True if alarm is in armed away state."""
        return self.get_armed_state() == ArmedState.ARMED_AWAY

    @property
    def is_armed_stay(self) -> bool:
        """Return True if alarm is in armed stay state."""
        return self.get_armed_state() == ArmedState.ARMED_STAY

    def get_armed_state(self):
        """Return the panel's arm state."""
        return self.data[Attribute.STATE]

    async def set_armed_state(self, state: int) -> None:
        """Set the armed state for a panel."""
        _LOGGER.debug("Setting %s to %s", self.name, ArmedState(state).name)
        await self.vivintskyapi.set_alarm_state(self.id, self.partition_id, state)

    async def disarm(self) -> None:
        """Disarm the alarm."""
        await self.set_armed_state(ArmedState.DISARMED)

    async def arm_stay(self) -> None:
        """Set the alarm to armed stay."""
        await self.set_armed_state(ArmedState.ARMED_STAY)

    async def arm_away(self) -> None:
        """Set the alarm to armed away."""
        await self.set_armed_state(ArmedState.ARMED_AWAY)

    async def get_panel_credentials(self) -> dict:
        """Get the panel credentials."""
        if not self.__panel_credentials:
            self.__panel_credentials = await self.vivintskyapi.get_panel_credentials(
                self.id
            )
        return self.__panel_credentials

    def get_devices(
        self,
        device_types: set[Type[VivintDevice]] = None,
    ) -> list[VivintDevice]:
        """Get a list of associated devices."""
        devices: list[VivintDevice] = None

        if device_types:
            devices = [
                device for device in self.devices if device.__class__ in device_types
            ]
        else:
            devices = self.devices

        return devices

    def refresh(self, data: dict[str, Any], new_device: bool = False) -> None:
        """Refresh the alarm panel."""
        if not new_device:
            self.update_data(data, override=True)
        else:
            self.data[Attribute.DEVICES].extend(data[Attribute.DEVICES])

        self.__parse_data(data)

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message."""
        operation = message.get(PubNubMessageAttribute.OPERATION)
        data = message.get(PubNubMessageAttribute.DATA)
        if not data:
            _LOGGER.debug(
                "Ignoring account partition message for panel %s, partition %s (no data provided): %s",
                self.id,
                self.partition_id,
                message,
            )
            return

        if not data.get(PubNubMessageAttribute.DEVICES):
            # this message is for the panel itself
            self.update_data(data)
        else:
            # this is a message for one (or more) of the attached devices
            devices_data = data[PubNubMessageAttribute.DEVICES]

            for device_data in devices_data:
                device_id = device_data.get("_id")
                if not device_id:
                    _LOGGER.debug("No device id")
                    continue

                if operation == PubNubOperatorAttribute.CREATE:
                    self.refresh(data=data, new_device=True)
                    add_async_job(self.handle_new_device, device_id)
                else:
                    device = first_or_none(
                        self.devices, lambda device: device.id == device_id
                    )
                    if not device:
                        _LOGGER.debug(
                            "Ignoring message for device %s (device not found)",
                            device_id,
                        )
                        continue

                    # for the sake of consistency, we also need to update the panel's raw data
                    raw_device_data = first_or_none(
                        self.data[Attribute.DEVICES],
                        lambda raw_device_data: raw_device_data["_id"]
                        == device_data["_id"],
                    )

                    if operation == PubNubOperatorAttribute.DELETE:
                        self.devices.remove(device)
                        self.data[Attribute.DEVICES].remove(raw_device_data)
                        self.unregistered_devices[device.id] = (
                            device.name,
                            device.device_type,
                        )
                        self.emit(DEVICE_DELETED, {"device": device})
                    else:
                        device.handle_pubnub_message(device_data)
                        raw_device_data.update(device_data)

    async def handle_new_device(self, device_id: int) -> None:
        """Handle a new device."""
        try:
            device = first_or_none(self.devices, lambda device: device.id == device_id)
            while not device.is_valid:
                await asyncio.sleep(1)
                if device.id in self.unregistered_devices:
                    return
            resp = await self.vivintskyapi.get_device_data(self.id, device_id)
            data = resp[SystemAttribute.SYSTEM][SystemAttribute.PARTITION][0]
            self.refresh(data, new_device=True)
            self.emit(DEVICE_DISCOVERED, {"device": device})
        except VivintSkyApiError:
            _LOGGER.error("Error getting new device data for device %s", device_id)

    def __parse_data(self, data: dict[str, Any], init: bool = False) -> None:
        """Parse the alarm panel data."""
        for device_data in data[Attribute.DEVICES]:
            device: VivintDevice = None
            if not init:
                device = first_or_none(
                    self.devices,
                    lambda device: device.id == device_data[Attribute.ID],
                )
            if device:
                device.update_data(device_data, override=True)
            else:
                self.__parse_device_data(device_data=device_data)

        if data.get(Attribute.UNREGISTERED):
            self.unregistered_devices: dict[int, tuple] = {
                device[Attribute.ID]: (
                    device[Attribute.NAME],
                    DeviceType(device[Attribute.TYPE]),
                )
                for device in data[Attribute.UNREGISTERED]
            }

    def __parse_device_data(self, device_data: dict[str, Any]) -> None:
        """Parse device data and optionally emit a device discovered event."""
        device_class = get_device_class(device_data[Attribute.TYPE])
        device = device_class(device_data, self)
        self.devices.append(device)

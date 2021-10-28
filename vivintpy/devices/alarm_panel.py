"""Module that implements the AlarmPanel class."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

from ..const import (
    AlarmPanelAttribute,
    PubNubMessageAttribute,
    PubNubOperatorAttribute,
    SystemAttribute,
)
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
        self.__panel_credentials = None

        # initialize devices
        self.devices = [
            get_device_class(device_data[AlarmPanelAttribute.TYPE])(device_data, self)
            for device_data in self.data[AlarmPanelAttribute.DEVICES]
        ]

        # store a reference to the physical panel device
        self.__panel = first_or_none(
            self.devices,
            lambda device: DeviceType(device.data.get(AlarmPanelAttribute.TYPE))
            == DeviceType.TOUCH_PANEL,
        )

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Instance of VivitSkyApi."""
        return self.system.vivintskyapi

    @property
    def id(self) -> int:
        """Panel's id."""
        return self.data[AlarmPanelAttribute.PANEL_ID]

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
        return self.data[AlarmPanelAttribute.PARTITION_ID]

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
        return self.data[AlarmPanelAttribute.STATE]

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

    def refresh(self, data: dict, new_device: bool = False) -> None:
        """Refresh the alarm panel."""
        if not new_device:
            self.update_data(data, override=True)
        else:
            self.data[AlarmPanelAttribute.DEVICES].extend(
                data[AlarmPanelAttribute.DEVICES]
            )

        # update associated devices
        for device_data in data[AlarmPanelAttribute.DEVICES]:
            device = first_or_none(
                self.devices,
                lambda device: device.id == device_data[AlarmPanelAttribute.ID],
            )
            if device:
                device.update_data(device_data, override=True)
            else:
                device = get_device_class(device_data[AlarmPanelAttribute.TYPE])(
                    device_data, self
                )
                self.devices.append(device)
                self.emit(DEVICE_DISCOVERED, device_data)

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
                        self.data[AlarmPanelAttribute.DEVICES],
                        lambda raw_device_data: raw_device_data["_id"]
                        == device_data["_id"],
                    )

                    if operation == PubNubOperatorAttribute.DELETE:
                        self.devices.remove(device)
                        self.data[AlarmPanelAttribute.DEVICES].remove(raw_device_data)
                        self.emit(DEVICE_DELETED, raw_device_data)
                    else:
                        device.handle_pubnub_message(device_data)
                        raw_device_data.update(device_data)

    async def handle_new_device(self, device_id: int) -> None:
        """Handle a new device."""
        try:
            resp = await self.vivintskyapi.get_device_data(self.id, device_id)
            data = resp[SystemAttribute.SYSTEM][SystemAttribute.PARTITION][0]
            self.refresh(data, new_device=True)
        except VivintSkyApiError:
            _LOGGER.error("Error getting new device data for device %s", device_id)

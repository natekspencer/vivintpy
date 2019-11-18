"""Module that implements the AlarmPanel class."""
import logging
from typing import List, Set

from pyvivint.devices import VivintDevice, UnknownDevice, get_device_class
from pyvivint.enums import (
    ArmedStates,
    AlarmPanelAttributes as Attributes,
    PubNumMessageAttributes as MessageAttributes,
)
from pyvivint.utils import first_or_none
import pyvivint.vivintskyapi


_LOGGER = logging.getLogger(__name__)


class AlarmPanel(VivintDevice):
    """Describe a Vivint alarm panel."""

    def __init__(self, data: dict, system):
        super().__init__(data)
        self.system = system

        # initialize devices
        self.devices: List[VivintDevice] = [
            get_device_class(device_data[Attributes.DeviceType])(device_data, self)
            for device_data in self.data[Attributes.Devices]
        ]

    @property
    def vivintskyapi(self) -> pyvivint.vivintskyapi.VivintSkyApi:
        """Instance of VivitSkyApi."""
        return self.system.vivintskyapi

    @property
    def id(self) -> int:
        """Panel's id."""
        return self.data[Attributes.PanelId]

    @property
    def partition_id(self) -> int:
        """Panel's partition id."""
        return self.data[Attributes.PartitionId]

    @property
    def is_disarmed(self) -> bool:
        """Return True if alarm is disarmed."""
        return self.get_armed_state() == ArmedStates.Disarmed

    @property
    def is_armed_away(self) -> bool:
        """Return True if alarm is in armed away state."""
        return self.get_armed_state() == ArmedStates.ArmedAway

    def is_armed_stay(self) -> bool:
        """Return True if alarm is in armed stay state."""
        return self.get_armed_state() == ArmedStates.ArmedStay

    def get_armed_state(self):
        """Return the panel's arm state."""
        return self.data[Attributes.State]

    async def set_armed_state(self, state: int) -> None:
        """Set the armed state for a panel."""
        _LOGGER.debug(f"setting state: {ArmedStates.name(state)} for panel: {self.id}")
        await self.vivintskyapi.set_alarm_state(self.id, self.partition_id, state)

    async def disarm(self) -> None:
        """Disarm the alarm."""
        await self.set_armed_state(ArmedStates.Disarmed)

    async def arm_stay(self) -> None:
        """Set the alarm to armed stay."""
        await self.set_armed_state(ArmedStates.ArmedStay)

    async def arm_away(self) -> None:
        """Set the alarm to armed away."""
        await self.set_armed_state(ArmedStates.ArmedAway)

    def get_devices(self, device_types: Set[int] = None, include_unknown_devices: bool = False) -> List[VivintDevice]:
        """Get a list of associated devices."""
        devices = self.devices

        if device_types:
            devices = [
                device for device in self.devices if device.data[Attributes.DeviceType] in device_types
            ]

        if not include_unknown_devices:
            devices = [
                device for device in devices if not isinstance(device, UnknownDevice)
            ]

        return devices

    def refresh(self, data: dict) -> None:
        """Refreshes the alarm panel."""
        self.update_data(data, override=True)

        # update all associated devices
        for device_data in self.data[Attributes.Devices]:
            device = first_or_none(
                    self.devices, lambda device: device.id == device_data[Attributes.Id]
            )
            if device:
                device.update_data(device_data, override=True)
            else:
                device = get_device_class(device_data[Attributes.DeviceType])(device_data, self)
                self.devices.append(device)

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""
        data = message.get(MessageAttributes.Data)
        if not data:
            _LOGGER.debug(
                f"ignoring account_partition message for panel {self.id}, partition {self.partition_id} - "
                "no data provided"
            )
            return

        if not data.get(MessageAttributes.Devices):
            # this message is for the panel itself
            self.update_data(data)
        else:
            # this is a message for one (or more) of the attached devices
            devices_data = data[MessageAttributes.Devices]

            for device_data in devices_data:
                device_id = device_data.get("_id")
                if not device_id:
                    _LOGGER.debug("no device id")
                    continue

                device = first_or_none(
                    self.devices, lambda device: device.id == device_id
                )
                if not device:
                    _LOGGER.debug(
                        f"ignoring message for device {device_id}. Device not found"
                    )
                    continue

                device.handle_pubnub_message(device_data)

                # for the sake of consistency, we need to also update the panel's raw data
                raw_device_data = first_or_none(
                    self.data[Attributes.Devices],
                    lambda raw_device_data: raw_device_data["_id"]
                    == device_data["_id"],
                )
                raw_device_data.update(device_data)

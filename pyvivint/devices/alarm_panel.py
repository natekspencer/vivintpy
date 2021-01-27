"""Module that implements the AlarmPanel class."""
import logging
from typing import List, Set

from pyvivint.constants import AlarmPanelAttribute as Attributes
from pyvivint.constants import PubNubMessageAttribute as MessageAttributes
from pyvivint.devices import UnknownDevice, VivintDevice, get_device_class
from pyvivint.enums import ArmedState, DeviceType
from pyvivint.utils import first_or_none
from pyvivint.vivintskyapi import VivintSkyApi

_LOGGER = logging.getLogger(__name__)


class AlarmPanel(VivintDevice):
    """Describe a Vivint alarm panel."""

    def __init__(self, data: dict, system: "pyvivint.system.System"):
        super().__init__(data)
        self.system = system
        self.__panel_credentials = None

        # initialize devices
        self.devices: List[VivintDevice] = [
            get_device_class(device_data[Attributes.TYPE])(device_data, self)
            for device_data in self.data[Attributes.DEVICES]
        ]

        # store a reference to the physical panel device
        self.__panel = first_or_none(
            self.devices,
            lambda device: DeviceType(device.data.get(Attributes.TYPE))
            == DeviceType.TOUCH_PANEL,
        )

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Instance of VivitSkyApi."""
        return self.system.vivintskyapi

    @property
    def id(self) -> int:
        """Panel's id."""
        return self.data[Attributes.PANEL_ID]

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
        """Return the model (panel type) of the physical panel."""
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
        return self.data[Attributes.PARTITION_ID]

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
        return self.data[Attributes.STATE]

    async def set_armed_state(self, state: int) -> None:
        """Set the armed state for a panel."""
        _LOGGER.debug(f"setting {self.name} to {ArmedState(state).name}")
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
        """Gets the panel credentials."""
        if not self.__panel_credentials:
            self.__panel_credentials = await self.vivintskyapi.get_panel_credentials(
                self.id
            )
        return self.__panel_credentials

    def get_devices(
        self, device_types: Set[int] = None, include_unknown_devices: bool = False
    ) -> List[VivintDevice]:
        """Get a list of associated devices."""
        devices = self.devices

        if device_types:
            devices = [
                device
                for device in self.devices
                if device.data[Attributes.TYPE] in device_types
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
        for device_data in self.data[Attributes.DEVICES]:
            device = first_or_none(
                self.devices, lambda device: device.id == device_data[Attributes.ID]
            )
            if device:
                device.update_data(device_data, override=True)
            else:
                device = get_device_class(device_data[Attributes.TYPE])(
                    device_data, self
                )
                self.devices.append(device)

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""
        data = message.get(MessageAttributes.DATA)
        if not data:
            _LOGGER.debug(
                f"ignoring account_partition message for panel {self.id}, partition {self.partition_id} - "
                "no data provided"
            )
            return

        if not data.get(MessageAttributes.DEVICES):
            # this message is for the panel itself
            self.update_data(data)
        else:
            # this is a message for one (or more) of the attached devices
            devices_data = data[MessageAttributes.DEVICES]

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
                    self.data[Attributes.DEVICES],
                    lambda raw_device_data: raw_device_data["_id"]
                    == device_data["_id"],
                )
                raw_device_data.update(device_data)

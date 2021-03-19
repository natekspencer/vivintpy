"""This package contains the various devices attached to a Vivint system."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from ..const import VivintDeviceAttribute as Attribute
from ..entity import Entity
from ..enums import CapabilityCategoryType, CapabilityType
from ..vivintskyapi import VivintSkyApi
from ..zjs_device_config_db import get_zwave_device_info

if TYPE_CHECKING:
    from .alarm_panel import AlarmPanel

DEVICE = "device"


def get_device_class(device_type: str) -> Callable:
    """Maps a device_type string to the class that implements that device."""
    from ..enums import DeviceType
    from . import UnknownDevice
    from .camera import Camera
    from .door_lock import DoorLock
    from .garage_door import GarageDoor
    from .switch import BinarySwitch, MultilevelSwitch
    from .thermostat import Thermostat
    from .wireless_sensor import WirelessSensor

    mapping = {
        DeviceType.BINARY_SWITCH: BinarySwitch,
        DeviceType.CAMERA: Camera,
        DeviceType.DOOR_LOCK: DoorLock,
        DeviceType.GARAGE_DOOR: GarageDoor,
        DeviceType.MULTILEVEL_SWITCH: MultilevelSwitch,
        DeviceType.THERMOSTAT: Thermostat,
        DeviceType.WIRELESS_SENSOR: WirelessSensor,
    }

    return mapping.get(DeviceType(device_type), UnknownDevice)


class VivintDevice(Entity):
    """Class to implement a generic vivint device."""

    def __init__(self, data: dict, alarm_panel: AlarmPanel = None) -> None:
        super().__init__(data)
        self.alarm_panel = alarm_panel
        self._manufacturer = None
        self._model = None
        self._capabilities = (
            {
                CapabilityCategoryType(capability_category.get(Attribute.TYPE)): [
                    CapabilityType(capability)
                    for capability in capability_category.get(Attribute.CAPABILITY)
                ]
                for capability_category in data.get(Attribute.CAPABILITY_CATEGORY)
            }
            if data.get(Attribute.CAPABILITY_CATEGORY)
            else None
        )

    def __repr__(self) -> str:
        """Custom repr method"""
        return f"<{self.__class__.__name__} {self.id}, {self.name}>"

    @property
    def id(self) -> int:
        """Device's id."""
        return self.data[Attribute.ID]

    @property
    def name(self) -> Optional[str]:
        """Device's name."""
        return self.data.get(Attribute.NAME)

    @property
    def capabilities(
        self,
    ) -> Optional[Dict[CapabilityCategoryType, List[CapabilityType]]]:
        """Device capabilities."""
        return self._capabilities

    @property
    def manufacturer(self) -> Optional[str]:
        """Return the manufacturer for this device."""
        if not self._manufacturer and self.data.get("zpd"):
            self.get_zwave_details()
        return self._manufacturer

    @property
    def model(self) -> Optional[str]:
        """Return the model for this device."""
        if not self._model and self.data.get("zpd"):
            self.get_zwave_details()
        return self._model

    @property
    def panel_id(self) -> int:
        """Return the id of the panel this device is associated to."""
        return self.data.get(Attribute.PANEL_ID)

    @property
    def serial_number(self) -> Optional[str]:
        """Return the serial number for this device."""
        serial_number = self.data.get(Attribute.SERIAL_NUMBER_32_BIT)
        serial_number = (
            serial_number if serial_number else self.data.get(Attribute.SERIAL_NUMBER)
        )
        return serial_number

    @property
    def software_version(self) -> str:
        """Return the software version of this device, if any."""
        # panels
        current_software_version = self.data.get(Attribute.CURRENT_SOFTWARE_VERSION)
        # z-wave devices (some)
        firmware_version = (
            ".".join(
                [
                    str(i)
                    for s in self.data.get(Attribute.FIRMWARE_VERSION) or []
                    for i in s
                ]
            )
            or None
        )
        return current_software_version or firmware_version

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Instance of VivintSkyApi."""
        assert self.alarm_panel, """no alarm panel set for this device"""
        return self.alarm_panel.system.vivintskyapi

    def get_zwave_details(self):
        if self.data.get("zpd") is None:
            return None

        result = get_zwave_device_info(
            self.data.get("manid"),
            self.data.get("prtid"),
            self.data.get("prid"),
        )

        self._manufacturer = result.get("manufacturer", "Unknown")

        label = result.get("label")
        description = result.get("description")

        if label and description:
            self._model = f"{description} ({label})"
        elif label:
            self._model = label
        elif description:
            self._model = description
        else:
            self._model = "Unknown"

        return [self._manufacturer, self._model]

    def emit(self, event_name: str, data: dict) -> None:
        """Add device data and then send to parent."""
        if data.get(DEVICE) is None:
            data.update({DEVICE: self})

        super().emit(event_name, data)


class UnknownDevice(VivintDevice):
    """Describe an unknown/unsupported vivint device."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}|{self.data[Attribute.TYPE]} {self.id}>"

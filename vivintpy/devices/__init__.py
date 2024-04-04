"""This package contains the various devices attached to a Vivint system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type, cast

from ..const import VivintDeviceAttribute as Attribute
from ..entity import Entity
from ..enums import (
    CapabilityCategoryType,
    CapabilityType,
    DeviceType,
    FeatureType,
    ZoneBypass,
)
from ..utils import send_deprecation_warning
from ..vivintskyapi import VivintSkyApi
from ..zjs_device_config_db import get_zwave_device_info

if TYPE_CHECKING:
    from .alarm_panel import AlarmPanel

DEVICE = "device"


def get_device_class(device_type: str) -> Type[VivintDevice]:
    """Map a device_type string to the class that implements that device."""
    # pylint: disable=import-outside-toplevel,cyclic-import
    from .camera import Camera
    from .door_lock import DoorLock
    from .garage_door import GarageDoor
    from .switch import BinarySwitch, MultilevelSwitch
    from .thermostat import Thermostat
    from .wireless_sensor import WirelessSensor

    mapping: dict[DeviceType, Type[VivintDevice]] = {
        DeviceType.BINARY_SWITCH: BinarySwitch,
        DeviceType.CAMERA: Camera,
        DeviceType.DOOR_LOCK: DoorLock,
        DeviceType.GARAGE_DOOR: GarageDoor,
        DeviceType.MULTI_LEVEL_SWITCH: MultilevelSwitch,
        DeviceType.THERMOSTAT: Thermostat,
        DeviceType.PANEL: VivintDevice,
        DeviceType.WIRELESS_SENSOR: WirelessSensor,
    }

    return mapping.get(DeviceType(device_type), UnknownDevice)


class VivintDevice(Entity):
    """Class to implement a generic vivint device."""

    def __init__(self, data: dict, alarm_panel: AlarmPanel | None = None) -> None:
        """Initialize a device."""
        super().__init__(data)
        self.alarm_panel = alarm_panel
        self._manufacturer: str | None = None
        self._model: str | None = None
        self._capabilities = (
            {
                CapabilityCategoryType(capability_category.get(Attribute.TYPE)): [
                    CapabilityType(capability)
                    for capability in capability_category.get(Attribute.CAPABILITY)
                ]
                for capability_category in caca
            }
            if (caca := data.get(Attribute.CAPABILITY_CATEGORY)) is not None
            else None
        )
        self._features = (
            [FeatureType(feature) for feature in feats if feats.get(feature) is True]
            if (feats := data.get(Attribute.FEATURES)) is not None
            else None
        )
        self._parent: VivintDevice | None = None

    def __repr__(self) -> str:
        """Return custom __repr__ of device."""
        return f"<{self.__class__.__name__} {self.id}, {self.name}>"

    @property
    def api(self) -> VivintSkyApi:
        """Return the API."""
        assert self.alarm_panel, """no alarm panel set for this device"""
        return self.alarm_panel.system.api

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """Device's id."""
        return int(self.data[Attribute.ID])

    @property
    def is_valid(self) -> bool:
        """Return `True` if the device is valid."""
        return True

    @property
    def name(self) -> str | None:
        """Device's name."""
        return self.data.get(Attribute.NAME)

    @property
    def battery_level(self) -> int | None:
        """Return the device's battery level."""
        if not self.has_battery:
            return None
        if (battery_level := self.data.get(Attribute.BATTERY_LEVEL)) not in (None, ""):
            return battery_level
        return 0 if self.low_battery else 100

    @property
    def capabilities(
        self,
    ) -> dict[CapabilityCategoryType, list[CapabilityType]] | None:
        """Device capabilities."""
        return self._capabilities

    @property
    def device_type(self) -> DeviceType:
        """Return the device type."""
        return DeviceType(self.data.get(Attribute.TYPE))

    @property
    def features(self) -> list[FeatureType] | None:
        """Device Features."""
        return self._features

    @property
    def has_battery(self) -> bool:
        """Return `True` if the device has battery details."""
        return (
            self.data.get(Attribute.BATTERY_LEVEL) is not None
            or self.data.get(Attribute.LOW_BATTERY) is not None
        )

    @property
    def is_subdevice(self) -> bool:
        """Return if this device is a subdevice."""
        return self._parent is not None

    @property
    def low_battery(self) -> bool | None:
        """Return `True` if the device's battery level is low."""
        return self.data.get(Attribute.LOW_BATTERY, False) if self.has_battery else None

    @property
    def manufacturer(self) -> str | None:
        """Return the manufacturer for this device."""
        if not self._manufacturer and self.data.get("zpd"):
            self.get_zwave_details()
        return self._manufacturer

    @property
    def model(self) -> str | None:
        """Return the model for this device."""
        if not self._model and self.data.get("zpd"):
            self.get_zwave_details()
        return self._model

    @property
    def panel_id(self) -> int:
        """Return the id of the panel this device is associated to."""
        return int(self.data[Attribute.PANEL_ID])

    @property
    def parent(self) -> VivintDevice | None:
        """Return the parent device, if any."""
        return self._parent

    @property
    def serial_number(self) -> str | None:
        """Return the serial number for this device."""
        serial_number = self.data.get(Attribute.SERIAL_NUMBER_32_BIT)
        if not serial_number:
            serial_number = self.data.get(Attribute.SERIAL_NUMBER)
        return serial_number

    @property
    def software_version(self) -> str | None:
        """Return the software version of this device, if any."""
        # current software version
        if (csv := self.data.get(Attribute.CURRENT_SOFTWARE_VERSION)) is not None:
            return str(csv)
        # firmware version
        return (
            ".".join([str(i) for s in fwv for i in s])
            if (fwv := self.data.get(Attribute.FIRMWARE_VERSION)) is not None
            else None
        )

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Instance of VivintSkyApi."""
        send_deprecation_warning("vivintskyapi", "api")
        return self.api

    def get_zwave_details(self) -> None:
        """Get Z-Wave details."""
        if self.data.get("zpd") is None:
            return

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

    def emit(self, event_name: str, data: dict) -> None:
        """Add device data and then send to parent."""
        if data.get(DEVICE) is None:
            data.update({DEVICE: self})

        super().emit(event_name, data)


class BypassTamperDevice(VivintDevice):
    """Class for devices that can be bypassed and tampered."""

    @property
    def is_bypassed(self) -> bool:
        """Return True if the device is bypassed."""
        return (
            int(self.data.get(Attribute.BYPASSED, ZoneBypass.UNBYPASSED))
            != ZoneBypass.UNBYPASSED
        )

    @property
    def is_tampered(self) -> bool:
        """Return True if the device is reporting as tampered."""
        return cast(bool, self.data.get(Attribute.TAMPER, False))


class UnknownDevice(VivintDevice):
    """Describe an unknown/unsupported vivint device."""

    def __repr__(self) -> str:
        """Return custom __repr__ of device."""
        return f"<{self.__class__.__name__}|{self.data[Attribute.TYPE]} {self.id}, {self.name}>"

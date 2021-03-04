"""This package contains the various devices attached to a Vivint system."""
from __future__ import annotations

import asyncio
import concurrent.futures
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from ..const import VivintDeviceAttribute as Attribute
from ..entity import Entity
from ..enums import CapabilityCategoryType, CapabilityType
from ..vivintskyapi import VivintSkyApi

if TYPE_CHECKING:
    from .alarm_panel import AlarmPanel


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

    def __init__(self, data: dict, alarm_panel: AlarmPanel = None):
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

    def __repr__(self):
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
    def manufacturer(self):
        """Return the manufacturer for this device."""
        if not self._manufacturer and self.data.get("zpd"):
            self.get_zwave_details()
        return self._manufacturer

    @property
    def model(self):
        """Return the model for this device."""
        if not self._model and self.data.get("zpd"):
            self.get_zwave_details()
        return self._model

    @property
    def serial_number(self) -> str:
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

        pool = concurrent.futures.ThreadPoolExecutor()
        result = pool.submit(asyncio.run, self.get_zwave_details_async()).result()
        return result

    async def get_zwave_details_async(self):
        manufacturer_id = f"{self.data.get('manid'):04x}"
        product_id = f"{self.data.get('prid'):04x}"
        product_type_id = f"{self.data.get('prtid'):04x}"
        result = await self.vivintskyapi.get_zwave_details(
            manufacturer_id, product_id, product_type_id
        )
        [self._manufacturer, self._model] = result
        return result


class UnknownDevice(VivintDevice):
    """Describe an unknown/unsupported vivint device."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}|{self.data[Attribute.TYPE]} {self.id}>"

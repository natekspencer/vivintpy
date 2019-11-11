"""This package contains the various devices attached to a vivint system."""
from typing import Callable

from pyvivint.enums import DeviceTypes, VivintDeviceAttributes as Attributes
from pyvivint.entity import Entity
import pyvivint.vivintskyapi


def get_device_class(device_type: str) -> Callable:
    """Maps a device_type string to the class that implements that device."""
    from pyvivint.devices import UnknownDevice
    from pyvivint.devices.camera import Camera
    from pyvivint.devices.door_lock import DoorLock
    from pyvivint.devices.wireless_sensor import WirelessSensor

    mapping = {
        DeviceTypes.Camera: Camera,
        DeviceTypes.DoorLock: DoorLock,
        DeviceTypes.WirelessSensor: WirelessSensor
    }

    return mapping.get(device_type, UnknownDevice)


class VivintDevice(Entity):
    """Class to implement a generic vivint device."""
    def __init__(self, data: dict, alarm_panel: 'pyvivint.devices.alarm_panel.AlarmPanel' = None):
        super().__init__(data)
        self.alarm_panel = alarm_panel

    def __repr__(self):
        """Custom repr method"""
        return f'<{self.__class__.__name__} {self.id}, {self.name}>'

    @property
    def id(self) -> int:
        """Device's id."""
        return self.data[Attributes.Id]

    @property
    def name(self) -> str:
        """Device's name."""
        return self.data[Attributes.Name]

    @property
    def vivintskyapi(self) -> pyvivint.vivintskyapi.VivintSkyApi:
        """Instance of VivintSkyApi."""
        assert self.alarm_panel, """no alarm panel set for this device"""
        return self.alarm_panel.system.vivintskyapi


class UnknownDevice(VivintDevice):
    """Describe an unknown/unsupported vivint device."""

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}|{self.data[Attributes.DeviceType]} {self.id}>'

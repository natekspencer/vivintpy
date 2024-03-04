"""Test the devices."""
from vivintpy.devices import get_device_class
from vivintpy.devices.switch import BinarySwitch
from vivintpy.enums import DeviceType


def test_get_device_class() -> None:
    """Test get device class."""
    assert get_device_class(DeviceType.BINARY_SWITCH.value) == BinarySwitch

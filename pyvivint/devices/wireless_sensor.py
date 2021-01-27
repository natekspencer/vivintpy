"""Module that implements the WirelessSensor class."""
import logging

from pyvivint.constants import WirelessSensorAttribute as Attributes
from pyvivint.devices import VivintDevice
from pyvivint.enums import EquipmentCode, EquipmentType, SensorType

_LOGGER = logging.getLogger(__name__)


class WirelessSensor(VivintDevice):
    """Represents a Vivint wireless sensor device."""

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}|{self.equipment_type} {self.id}, {self.name}>"
        )

    @property
    def model(self) -> str:
        """Return the equipment_code as the model of this sensor."""
        return self.equipment_code.name

    @property
    def software_version(self) -> str:
        """Return the software version of this device, if any."""
        return self.data.get(Attributes.SENSOR_FIRMWARE_VERSION) or None

    @property
    def battery_level(self) -> int:
        """Sensor's battery level."""
        battery_level = self.data.get(Attributes.BATTERY_LEVEL)
        return (
            battery_level
            if battery_level is not None
            else 0
            if self.low_battery
            else 100
        )

    @property
    def equipment_code(self):
        """Return the equipment code of this sensor."""
        return EquipmentCode(self.data.get(Attributes.EQUIPMENT_CODE))

    @property
    def equipment_type(self):
        """Return the equipment type of this sensor."""
        return EquipmentType(self.data.get(Attributes.EQUIPMENT_TYPE))

    @property
    def sensor_type(self):
        """Return the sensor type of this sensor."""
        return SensorType(self.data.get(Attributes.SENSOR_TYPE))

    @property
    def is_bypassed(self) -> bool:
        """Return True if the sensor is bypassed."""
        return self.data[Attributes.BYPASSED] != 0

    @property
    def is_on(self) -> bool:
        """Return True if the sensor's state is on."""
        return self.data[Attributes.STATE]

    @property
    def low_battery(self) -> bool:
        """Return true if battery's level is low."""
        return self.data[Attributes.LOW_BATTERY]

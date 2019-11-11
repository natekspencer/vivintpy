"""Module that implements the WirelessSensor class."""
import logging

from pyvivint.devices import VivintDevice
from pyvivint.enums import WirelessSensorAttributes as Attributes


_LOGGER = logging.getLogger(__name__)


class WirelessSensor(VivintDevice):
    """Represents a Vivint wireless sensor device."""

    DEVICE_TYPE_TO_EQUIPMENT_CODE = {
        'COSensor': ['1026', '1266', '692'],
        'EntrySensor': ['1251', '1252', '862', '863', '655'],
        'FloodSensor': ['1128', '1264', '556'],
        'GarageDoor': ['1061', '2831'],
        'GlassBreakSensor': ['1248', '475', '864'],
        'HeatSensor': ['708'],
        'KeyFob': ['866', '577', '1250'],
        'Keypad': ['867'],
        'MotionSensor': ['1249', '609'],
        'PanicSensor': ['1253', '561', '868'],
        'Sensor': [
            '2830',
            '2832',
            '873',
            '941',
            '1208',
            '2081',
            '1144',
            '869',
            '1063',
            '1269',
            '0',
        ],
        'SmokeSensor': ['1058', '1066', '1267', '616'],
    }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}|{self.device_class} {self.id}, {self.name}>'

    @property
    def battery_level(self) -> int:
        """Sensor's battery level."""
        return self.data[Attributes.BatteryLevel]

    @property
    def device_class(self):
        equipment_code = self.data.get(Attributes.EquipmentCode)
        if not equipment_code:
            _LOGGER.debug("device has no equipment code")
            return

        for device_type, codes in self.DEVICE_TYPE_TO_EQUIPMENT_CODE.items():
            if str(equipment_code) in codes:
                return device_type

    @property
    def is_bypassed(self) -> bool:
        """Return True if the sensor is bypassed."""
        return self.data[Attributes.IdBypassed]

    @property
    def is_on(self) -> bool:
        """Return True if the sensor's state is on."""
        return self.data[Attributes.State]

    @property
    def low_battery(self) -> bool:
        """Return true if battery's level is low."""
        return self.data[Attributes.LowBattery]

    @property
    def serial_number(self) -> str:
        """Return sensor' serial number."""
        return self.data[Attributes.SerialNumber]

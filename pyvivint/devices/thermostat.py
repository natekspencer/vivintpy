"""Module that implements the Thermostat class."""
import logging

from ..const import ThermostatAttribute as Attribute
from ..enums import FanMode, HoldMode, OperatingMode
from . import VivintDevice
from .alarm_panel import AlarmPanel

_LOGGER = logging.getLogger(__name__)

NEST_DEVICE = "pod_nest_thermostat_device"


class Thermostat(VivintDevice):
    """Represents a Vivint thermostat device."""

    def __init__(self, data: dict, alarm_panel: AlarmPanel):
        """Initialize a thermostat."""
        super().__init__(data, alarm_panel)

        if data.get(Attribute.ACTUAL_TYPE) == NEST_DEVICE:
            [self._manufacturer, self._model] = ["Google", "Nest"]

    @property
    def cool_set_point(self) -> float:
        return self.data.get(Attribute.COOL_SET_POINT)

    @property
    def fan_mode(self) -> FanMode:
        return FanMode(self.data.get(Attribute.FAN_MODE))

    @property
    def heat_set_point(self) -> float:
        return self.data.get(Attribute.HEAT_SET_POINT)

    @property
    def hold_mode(self) -> HoldMode:
        return HoldMode(self.data.get(Attribute.HOLD_MODE))

    @property
    def humidity(self) -> int:
        return self.data.get(Attribute.HUMIDITY)

    @property
    def is_fan_on(self) -> bool:
        return self.data.get(Attribute.FAN_STATE) == 1

    @property
    def is_on(self) -> int:
        return self.data.get(Attribute.OPERATING_STATE) == 1

    @property
    def maximum_temperature(self) -> float:
        return self.data.get(Attribute.MAXIMUM_TEMPERATURE)

    @property
    def minimum_temperature(self) -> float:
        return self.data.get(Attribute.MINIMUM_TEMPERATURE)

    @property
    def operating_mode(self) -> OperatingMode:
        return OperatingMode(self.data.get(Attribute.OPERATING_MODE))

    @property
    def temperature(self) -> float:
        return self.data.get(Attribute.CURRENT_TEMPERATURE)

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> int:
        """Converts Celsius to Fahrenheit"""
        return round(celsius * 1.8 + 32)

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message directed to this entity."""
        super().handle_pubnub_message(message)

        _LOGGER.debug(f"{self.name} updated")

    async def set_state(self, **kwargs) -> None:
        """Set the state of the thermostat."""
        await self.vivintskyapi.set_thermostat_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, **kwargs
        )

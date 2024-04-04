"""Module that implements the Thermostat class."""

from __future__ import annotations

import logging
from typing import Any

from ..const import ThermostatAttribute as Attribute
from ..enums import DeviceType, FanMode, HoldMode, OperatingMode, OperatingState
from . import VivintDevice
from .alarm_panel import AlarmPanel

_LOGGER = logging.getLogger(__name__)


class Thermostat(VivintDevice):
    """Represents a Vivint thermostat device."""

    def __init__(self, data: dict, alarm_panel: AlarmPanel):
        """Initialize a thermostat."""
        super().__init__(data, alarm_panel)

        if data.get(Attribute.ACTUAL_TYPE) == DeviceType.POD_NEST_THERMOSTAT.value:
            [self._manufacturer, self._model] = ["Google", "Nest"]

    @property
    def cool_set_point(self) -> float | None:
        """Return the cool set point of the thermostat."""
        return self.data.get(Attribute.COOL_SET_POINT)

    @property
    def fan_mode(self) -> FanMode:
        """Return the fan mode of the thermostat."""
        return FanMode(self.data.get(Attribute.FAN_MODE))  # type: ignore

    @property
    def heat_set_point(self) -> float | None:
        """Return the heat set point of the thermostat."""
        return self.data.get(Attribute.HEAT_SET_POINT)

    @property
    def hold_mode(self) -> HoldMode:
        """Return the hold mode of the thermostat."""
        return HoldMode(self.data.get(Attribute.HOLD_MODE))  # type: ignore

    @property
    def humidity(self) -> int | None:
        """Return the humidity of the thermostat."""
        return self.data.get(Attribute.HUMIDITY)

    @property
    def is_fan_on(self) -> bool:
        """Return `True` if the thermostat fan is on."""
        return self.data.get(Attribute.FAN_STATE) == 1

    @property
    def is_on(self) -> bool:
        """Return `True` if the thermostat is on."""
        return self.operating_state != OperatingState.IDLE

    @property
    def maximum_temperature(self) -> float | None:
        """Return the maximum temperature of the thermostat."""
        return self.data.get(Attribute.MAXIMUM_TEMPERATURE)

    @property
    def minimum_temperature(self) -> float | None:
        """Return the minimum temperature of the thermostat."""
        return self.data.get(Attribute.MINIMUM_TEMPERATURE)

    @property
    def operating_mode(self) -> OperatingMode:
        """Return the operating mode of the thermostat."""
        return OperatingMode(self.data.get(Attribute.OPERATING_MODE))  # type: ignore

    @property
    def operating_state(self) -> OperatingState:
        """Return the operating state of the thermostat."""
        return OperatingState(self.data.get(Attribute.OPERATING_STATE))  # type: ignore

    @property
    def temperature(self) -> float | None:
        """Return the temperature of the thermostat."""
        return self.data.get(Attribute.CURRENT_TEMPERATURE)

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> int:
        """Convert Celsius to Fahrenheit."""
        return round(celsius * 1.8 + 32)

    async def set_state(self, **kwargs: Any) -> None:
        """Set the state of the thermostat."""
        assert self.alarm_panel
        await self.api.set_thermostat_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, **kwargs
        )

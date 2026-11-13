"""Module that implements the ClimateThermostat class."""

from __future__ import annotations

from typing import Any

from ..const import ThermostatAttribute as Attribute
from ..enums import (
    CapabilityCategoryType,
    CapabilityType,
    DeviceType,
    FanMode,
    HoldMode,
    OperatingMode,
    OperatingState,
)
from ..proto import climate_pb2
from .alarm_panel import AlarmPanel
from .thermostat import Thermostat

Component = climate_pb2.Component

# fan modes by the name the climate service uses for them
FAN_MODES = {
    "AUTO_LOW": FanMode.AUTO_LOW,
    "ON_LOW": FanMode.ON_LOW,
    "AUTO_HIGH": FanMode.AUTO_HIGH,
    "ON_HIGH": FanMode.ON_HIGH,
    "FIFTEEN_MINUTE": FanMode.TIMER_15,
    "THIRTY_MINUTE": FanMode.TIMER_30,
    "FORTY_FIVE_MINUTE": FanMode.TIMER_45,
    "SIXTY_MINUTE": FanMode.TIMER_60,
    "ONE_TWENTY_MINUTE": FanMode.TIMER_120,
    "TWO_FORTY_MINUTE": FanMode.TIMER_240,
    "FOUR_EIGHTY_MINUTE": FanMode.TIMER_480,
    "SEVEN_TWENTY_MINUTE": FanMode.TIMER_720,
    "NINE_SIXTY_MINUTE": FanMode.TIMER_960,
}
FAN_MODE_NAMES = {mode: name for name, mode in FAN_MODES.items()}

FAN_TIMER_CAPABILITIES = {
    FanMode.TIMER_15: CapabilityType.FAN15_MINUTE,
    FanMode.TIMER_30: CapabilityType.FAN30_MINUTE,
    FanMode.TIMER_45: CapabilityType.FAN45_MINUTE,
    FanMode.TIMER_60: CapabilityType.FAN60_MINUTE,
    FanMode.TIMER_120: CapabilityType.FAN120_MINUTE,
    FanMode.TIMER_240: CapabilityType.FAN240_MINUTE,
    FanMode.TIMER_480: CapabilityType.FAN480_MINUTE,
    FanMode.TIMER_960: CapabilityType.FAN960_MINUTE,
}

OPERATING_STATES = {
    "HEATING": OperatingState.HEATING,
    "COOLING": OperatingState.COOLING,
    "FAN_ON": OperatingState.FAN_ON,
    "ERROR": OperatingState.UNKNOWN,
    "UNKNOWN": OperatingState.UNKNOWN,
}


def _enum_name(enum_type: Any, value: int) -> str:
    """Return the name of an enum value, or `UNKNOWN` if the proto doesn't define it."""
    try:
        return str(enum_type.Name(value))
    except ValueError:
        return "UNKNOWN"


def _enum_value(enum_type: Any, name: str) -> int:
    """Return the value of an enum name, raising `ValueError` if it isn't defined."""
    try:
        return int(enum_type.Value(name))
    except ValueError:
        raise ValueError(f"Unsupported value: {name}") from None


def _set_value(value: float) -> float | None:
    """Return a proto3 double that has no presence tracking, `None` if it is unset."""
    return value or None


class ClimateThermostat(Thermostat):
    """Represents a thermostat managed by the Vivint climate service.

    This includes Google Nest thermostats linked to a Vivint system. Temperatures are
    in degrees Celsius.
    """

    def __init__(
        self,
        device: climate_pb2.ClimateDevice,
        alarm_panel: AlarmPanel,
        *,
        snapshot: bool = False,
    ) -> None:
        """Initialize a thermostat, from a full listing if `snapshot`."""
        self._device = device
        # `is_online` has no presence tracking, so only `True` and a full listing say
        # that the service reported it
        self._online_known = bool(device.is_online) or snapshot
        super().__init__(self._build_data(device, alarm_panel), alarm_panel)
        self._set_manufacturer()

    def _set_manufacturer(self) -> None:
        """Set the manufacturer and model from the kind of device."""
        if self._device.WhichOneof("details") == "nest_thermostat_device":
            [self._manufacturer, self._model] = ["Google", "Nest"]

    @staticmethod
    def _build_data(device: climate_pb2.ClimateDevice, alarm_panel: AlarmPanel) -> dict:
        """Return the raw data the base device classes expect."""
        return {
            Attribute.ID: device.id,
            Attribute.NAME: device.name,
            Attribute.PANEL_ID: alarm_panel.id,
            Attribute.TYPE: DeviceType.THERMOSTAT.value,
        }

    def update_device(
        self, device: climate_pb2.ClimateDevice, *, snapshot: bool = False
    ) -> None:
        """Apply a device update received from the service.

        An update only carries the components that changed, so they are merged into
        the components already known. A `snapshot` has all of them, so it replaces
        them and a component the device no longer has is dropped.
        """
        assert self.alarm_panel
        merged = climate_pb2.ClimateDevice()
        merged.CopyFrom(self._device)
        if device.name:
            merged.name = device.name
        # an update that carries the device's identity reports `is_online`, but an
        # unset one reads as `False`, so that is only believed when it can't be unset
        if (device.name or device.WhichOneof("details")) and (
            device.is_online or snapshot or self._online_known
        ):
            merged.is_online = device.is_online
            self._online_known = True
        if kind := device.WhichOneof("details"):
            getattr(merged, kind).CopyFrom(getattr(device, kind))
        components = (
            {}
            if snapshot
            else {component.id: component for component in merged.components}
        )
        components.update({component.id: component for component in device.components})
        del merged.components[:]
        merged.components.extend(components.values())
        self._device = merged
        self.update_data(self._build_data(merged, self.alarm_panel))

    def fill_from_snapshot(self, device: climate_pb2.ClimateDevice) -> None:
        """Add what a snapshot has that the updates received so far didn't carry.

        That is the components the thermostat doesn't have yet and, when the updates
        carried no identity, its name, details and whether it is online.
        """
        assert self.alarm_panel
        if not self._online_known:
            self._device.is_online = device.is_online
            self._online_known = True
        if not (self._device.name or self._device.WhichOneof("details")):
            self._device.temperature_units = device.temperature_units
        if not self._device.name:
            self._device.name = device.name
        if (kind := device.WhichOneof("details")) and not self._device.WhichOneof(
            "details"
        ):
            getattr(self._device, kind).CopyFrom(getattr(device, kind))
        known = {component.id for component in self._device.components}
        self._device.components.extend(
            component for component in device.components if component.id not in known
        )
        self._set_manufacturer()
        self.update_data(self._build_data(self._device, self.alarm_panel))

    def _component(self, kind: str) -> Any | None:
        """Return the component of the given kind, if the device has one."""
        for component in self._device.components:
            if component.WhichOneof("value") == kind:
                return getattr(component, kind)
        return None

    def _component_id(self, kind: str) -> str:
        """Return the id of the component of the given kind."""
        for component in self._device.components:
            if component.WhichOneof("value") == kind:
                return str(component.id)
        raise ValueError(f"{self.name} has no {kind} component")

    @property
    def id(self) -> str:  # type: ignore[override]
        """Device's id, a URN."""
        return str(self._device.id)

    @property
    def capabilities(
        self,
    ) -> dict[CapabilityCategoryType, list[CapabilityType]]:
        """Return the fan timers the thermostat supports."""
        fan_setting = self._component("fan_setting")
        modes = (
            [
                FAN_MODES.get(_enum_name(Component.FanSetting.Mode, mode))
                for mode in fan_setting.modes_supported
            ]
            if fan_setting
            else []
        )
        return {
            CapabilityCategoryType.THERMOSTAT: [
                FAN_TIMER_CAPABILITIES[mode]
                for mode in modes
                if mode in FAN_TIMER_CAPABILITIES
            ]
        }

    @property
    def is_online(self) -> bool:
        """Return `True` if the thermostat is online."""
        return bool(self._device.is_online)

    @property
    def serial_number(self) -> str | None:
        """Return the serial number of the thermostat."""
        info = self._component("device_info")
        return (info.serial_number or None) if info else None

    @property
    def software_version(self) -> str | None:
        """Return the firmware version of the thermostat."""
        info = self._component("device_info")
        return (info.firmware_version or None) if info else None

    @property
    def cool_set_point(self) -> float | None:
        """Return the cool set point of the thermostat."""
        setpoints = self._component("setpoints")
        return _set_value(setpoints.cool_setpoint) if setpoints else None

    @property
    def heat_set_point(self) -> float | None:
        """Return the heat set point of the thermostat."""
        setpoints = self._component("setpoints")
        return _set_value(setpoints.heat_setpoint) if setpoints else None

    @property
    def maximum_temperature(self) -> float | None:
        """Return the maximum temperature of the thermostat."""
        setpoints = self._component("setpoints")
        return _set_value(setpoints.maximum_temperature) if setpoints else None

    @property
    def minimum_temperature(self) -> float | None:
        """Return the minimum temperature of the thermostat."""
        setpoints = self._component("setpoints")
        return _set_value(setpoints.minimum_temperature) if setpoints else None

    @property
    def temperature(self) -> float | None:
        """Return the temperature of the thermostat."""
        detection = self._component("temperature_detection")
        return _set_value(detection.current_temperature) if detection else None

    @property
    def humidity(self) -> int | None:
        """Return the humidity of the thermostat."""
        detection = self._component("humidity_detection")
        value = _set_value(detection.value) if detection else None
        return int(value) if value is not None else None

    @property
    def fan_mode(self) -> FanMode:
        """Return the fan mode of the thermostat."""
        fan_setting = self._component("fan_setting")
        if not fan_setting:
            return FanMode.UNKNOWN
        return FAN_MODES.get(
            _enum_name(Component.FanSetting.Mode, fan_setting.current_mode),
            FanMode.UNKNOWN,
        )

    @property
    def is_fan_on(self) -> bool:
        """Return `True` if the thermostat fan is on."""
        fan_setting = self._component("fan_setting")
        return bool(fan_setting.is_on) if fan_setting else False

    @property
    def hold_mode(self) -> HoldMode:
        """Return the hold mode of the thermostat."""
        hold = self._component("hold_mode")
        if not hold:
            return HoldMode.UNKNOWN
        return HoldMode.__members__.get(
            _enum_name(Component.HoldMode.Mode, hold.mode), HoldMode.UNKNOWN
        )

    @property
    def operating_mode(self) -> OperatingMode:
        """Return the operating mode of the thermostat."""
        setting = self._component("operating_mode_setting")
        if not setting:
            return OperatingMode.UNKNOWN
        return OperatingMode.__members__.get(
            _enum_name(Component.OperatingModeSetting.Mode, setting.current_mode),
            OperatingMode.UNKNOWN,
        )

    @property
    def operating_state(self) -> OperatingState:
        """Return the operating state of the thermostat."""
        state = self._component("operating_state")
        if not state:
            return OperatingState.UNKNOWN
        return OPERATING_STATES.get(
            _enum_name(Component.OperatingState.State, state.current_state),
            OperatingState.IDLE,
        )

    async def set_state(self, **kwargs: Any) -> None:
        """Set the state of the thermostat."""
        heat = kwargs.pop(Attribute.HEAT_SET_POINT, None)
        cool = kwargs.pop(Attribute.COOL_SET_POINT, None)
        fan_mode = kwargs.pop(Attribute.FAN_MODE, None)
        operating_mode = kwargs.pop(Attribute.OPERATING_MODE, None)
        hold_mode = kwargs.pop(Attribute.HOLD_MODE, None)
        if kwargs:
            raise ValueError(f"Unsupported thermostat attributes: {', '.join(kwargs)}")

        # resolve every value before sending anything, so a bad one sends no RPCs
        requests: list[tuple[str, Any, str, dict[str, Any]]] = []
        if fan_mode is not None:
            name = FAN_MODE_NAMES.get(FanMode(fan_mode))
            if name is None:
                raise ValueError(f"Unsupported fan mode: {fan_mode!r}")
            requests.append(
                (
                    "SetFanMode",
                    climate_pb2.SetFanModeRequest,
                    "fan_setting",
                    {"mode": Component.FanSetting.Mode.Value(name)},
                )
            )
        if operating_mode is not None:
            requests.append(
                (
                    "SetOperatingMode",
                    climate_pb2.SetOperatingModeRequest,
                    "operating_mode_setting",
                    {
                        "mode": _enum_value(
                            Component.OperatingModeSetting.Mode,
                            OperatingMode(operating_mode).name,
                        )
                    },
                )
            )
        if hold_mode is not None:
            requests.append(
                (
                    "SetHoldMode",
                    climate_pb2.SetHoldModeRequest,
                    "hold_mode",
                    {
                        "mode": _enum_value(
                            Component.HoldMode.Mode, HoldMode(hold_mode).name
                        )
                    },
                )
            )
        for _, _, component, _ in requests:
            self._component_id(component)

        if heat is not None or cool is not None:
            await self.set_set_points(heat=heat, cool=cool)
        for method, request_type, component, fields in requests:
            await self._send(method, request_type, component, **fields)

    async def set_set_points(
        self, heat: float | None = None, cool: float | None = None
    ) -> None:
        """Set the heat and/or cool set points, in degrees Celsius."""
        if heat is not None and cool is not None:
            await self._send(
                "SetTemperatureSetpoints",
                climate_pb2.SetTemperatureSetpointsRequest,
                "setpoints",
                heat_celsius=heat,
                cool_celsius=cool,
            )
        elif cool is not None:
            await self._send(
                "SetCoolSetpoint",
                climate_pb2.SetCoolSetpointRequest,
                "setpoints",
                celsius=cool,
            )
        elif heat is not None:
            await self._send(
                "SetHeatSetpoint",
                climate_pb2.SetHeatSetpointRequest,
                "setpoints",
                celsius=heat,
            )

    async def _send(
        self, method: str, request_type: Any, component: str, **fields: Any
    ) -> None:
        """Send a request that targets one of the thermostat's components."""
        assert self.alarm_panel
        system = self.alarm_panel.system
        await self.api.climate_request(
            method,
            request_type(
                system_id=system.id,
                device_id=self.id,
                component_id=self._component_id(component),
                **fields,
            ),
        )
        system.request_climate_refresh()

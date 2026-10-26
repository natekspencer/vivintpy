import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DemandResponsePlatformSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEMAND_RESPONSE_PLATFORM_SOURCE_UNSPECIFIED: _ClassVar[DemandResponsePlatformSource]
    DEMAND_RESPONSE_PLATFORM_SOURCE_APP: _ClassVar[DemandResponsePlatformSource]
    DEMAND_RESPONSE_PLATFORM_SOURCE_CARE: _ClassVar[DemandResponsePlatformSource]

class OccupancyState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified: _ClassVar[OccupancyState]
    Home: _ClassVar[OccupancyState]
    Away: _ClassVar[OccupancyState]
    Sleep: _ClassVar[OccupancyState]
    Vacation: _ClassVar[OccupancyState]

class RetailElectricProvider(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED_PROVIDER: _ClassVar[RetailElectricProvider]
    RELIANT: _ClassVar[RetailElectricProvider]
    GME: _ClassVar[RetailElectricProvider]
    DE: _ClassVar[RetailElectricProvider]
    CIRRO: _ClassVar[RetailElectricProvider]
    DISCOUNT: _ClassVar[RetailElectricProvider]

class TimeZones(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[TimeZones]
    AMERICA_NEWYORK: _ClassVar[TimeZones]
    AMERICA_CHICAGO: _ClassVar[TimeZones]
    AMERICA_DENVER: _ClassVar[TimeZones]
    AMERICA_PHOENIX: _ClassVar[TimeZones]
    AMERICA_LOSANGELES: _ClassVar[TimeZones]
    AMERICA_ANCHORAGE: _ClassVar[TimeZones]
    PACIFIC_HONOLULU: _ClassVar[TimeZones]
DEMAND_RESPONSE_PLATFORM_SOURCE_UNSPECIFIED: DemandResponsePlatformSource
DEMAND_RESPONSE_PLATFORM_SOURCE_APP: DemandResponsePlatformSource
DEMAND_RESPONSE_PLATFORM_SOURCE_CARE: DemandResponsePlatformSource
Unspecified: OccupancyState
Home: OccupancyState
Away: OccupancyState
Sleep: OccupancyState
Vacation: OccupancyState
UNSPECIFIED_PROVIDER: RetailElectricProvider
RELIANT: RetailElectricProvider
GME: RetailElectricProvider
DE: RetailElectricProvider
CIRRO: RetailElectricProvider
DISCOUNT: RetailElectricProvider
UNSPECIFIED: TimeZones
AMERICA_NEWYORK: TimeZones
AMERICA_CHICAGO: TimeZones
AMERICA_DENVER: TimeZones
AMERICA_PHOENIX: TimeZones
AMERICA_LOSANGELES: TimeZones
AMERICA_ANCHORAGE: TimeZones
PACIFIC_HONOLULU: TimeZones

class Anomaly(_message.Message):
    __slots__ = ("vendor_device_id", "current_state", "last_detected_at", "detected_at", "observed_runtime_hours", "expected_runtime_hours", "excess_runtime_hours", "dismissed_at", "is_dismissed")
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STATE_FIELD_NUMBER: _ClassVar[int]
    LAST_DETECTED_AT_FIELD_NUMBER: _ClassVar[int]
    DETECTED_AT_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_RUNTIME_HOURS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_RUNTIME_HOURS_FIELD_NUMBER: _ClassVar[int]
    EXCESS_RUNTIME_HOURS_FIELD_NUMBER: _ClassVar[int]
    DISMISSED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_DISMISSED_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    current_state: Component.OperatingState.State
    last_detected_at: _timestamp_pb2.Timestamp
    detected_at: _timestamp_pb2.Timestamp
    observed_runtime_hours: int
    expected_runtime_hours: int
    excess_runtime_hours: int
    dismissed_at: _timestamp_pb2.Timestamp
    is_dismissed: bool
    def __init__(self, vendor_device_id: _Optional[str] = ..., current_state: _Optional[_Union[Component.OperatingState.State, str]] = ..., last_detected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., detected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., observed_runtime_hours: _Optional[int] = ..., expected_runtime_hours: _Optional[int] = ..., excess_runtime_hours: _Optional[int] = ..., dismissed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_dismissed: _Optional[bool] = ...) -> None: ...

class ClimateDevice(_message.Message):
    __slots__ = ("id", "name", "is_online", "components", "temperature_units", "ct100_thermostat_device", "ct200_thermostat_device", "ev2_thermostat_device", "nest_thermostat_device", "ev2z_thermostat_device", "pegasus_thermostat_device")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ONLINE_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNITS_FIELD_NUMBER: _ClassVar[int]
    CT100_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    CT200_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    EV2_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    NEST_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    EV2Z_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    PEGASUS_THERMOSTAT_DEVICE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    is_online: bool
    components: _containers.RepeatedCompositeFieldContainer[Component]
    temperature_units: GetGlobalSettingsResponse.TemperatureUnits
    ct100_thermostat_device: Ct100ThermostatDevice
    ct200_thermostat_device: Ct200ThermostatDevice
    ev2_thermostat_device: Ev2ThermostatDevice
    nest_thermostat_device: NestThermostatDevice
    ev2z_thermostat_device: Ev2ZThermostatDevice
    pegasus_thermostat_device: PegasusThermostatDevice
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., is_online: _Optional[bool] = ..., components: _Optional[_Iterable[_Union[Component, _Mapping]]] = ..., temperature_units: _Optional[_Union[GetGlobalSettingsResponse.TemperatureUnits, str]] = ..., ct100_thermostat_device: _Optional[_Union[Ct100ThermostatDevice, _Mapping]] = ..., ct200_thermostat_device: _Optional[_Union[Ct200ThermostatDevice, _Mapping]] = ..., ev2_thermostat_device: _Optional[_Union[Ev2ThermostatDevice, _Mapping]] = ..., nest_thermostat_device: _Optional[_Union[NestThermostatDevice, _Mapping]] = ..., ev2z_thermostat_device: _Optional[_Union[Ev2ZThermostatDevice, _Mapping]] = ..., pegasus_thermostat_device: _Optional[_Union[PegasusThermostatDevice, _Mapping]] = ...) -> None: ...

class Component(_message.Message):
    __slots__ = ("id", "temperature_detection", "setpoints", "fan_setting", "zwave_diagnostics", "humidity_detection", "setpoint_lock", "schedule", "operating_mode_setting", "operating_state", "battery", "humidity_mode", "humidity_setpoint", "deletable", "rebootable", "device_info", "hold_mode", "demand_response", "smart_comfort_targets", "online", "wi_fi")
    class OfflineReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Component.OfflineReason]
        POWER_OFF: _ClassVar[Component.OfflineReason]
        HARDWARE_FAILURE: _ClassVar[Component.OfflineReason]
        SOFTWARE_ERROR: _ClassVar[Component.OfflineReason]
        MAINTENANCE: _ClassVar[Component.OfflineReason]
        BRIDGE_OFFLINE: _ClassVar[Component.OfflineReason]
        MQTT_BROKER_ISSUES: _ClassVar[Component.OfflineReason]
        LOSS_OF_WIFI_OR_CELLULAR: _ClassVar[Component.OfflineReason]
        NETWORK_CONGESTION: _ClassVar[Component.OfflineReason]
        ROUTER_OR_MODEM_MALFUNCTION: _ClassVar[Component.OfflineReason]
        FIREWALL_OR_SECURITY_SETTINGS: _ClassVar[Component.OfflineReason]
        DNS_PROBLEMS: _ClassVar[Component.OfflineReason]
        IP_ADDRESS_CHANGE: _ClassVar[Component.OfflineReason]
        REBOOT: _ClassVar[Component.OfflineReason]
        SOFTWARE_UPDATE: _ClassVar[Component.OfflineReason]
        INVALID_VENDOR_TOKEN: _ClassVar[Component.OfflineReason]
    UNKNOWN: Component.OfflineReason
    POWER_OFF: Component.OfflineReason
    HARDWARE_FAILURE: Component.OfflineReason
    SOFTWARE_ERROR: Component.OfflineReason
    MAINTENANCE: Component.OfflineReason
    BRIDGE_OFFLINE: Component.OfflineReason
    MQTT_BROKER_ISSUES: Component.OfflineReason
    LOSS_OF_WIFI_OR_CELLULAR: Component.OfflineReason
    NETWORK_CONGESTION: Component.OfflineReason
    ROUTER_OR_MODEM_MALFUNCTION: Component.OfflineReason
    FIREWALL_OR_SECURITY_SETTINGS: Component.OfflineReason
    DNS_PROBLEMS: Component.OfflineReason
    IP_ADDRESS_CHANGE: Component.OfflineReason
    REBOOT: Component.OfflineReason
    SOFTWARE_UPDATE: Component.OfflineReason
    INVALID_VENDOR_TOKEN: Component.OfflineReason
    class Deletable(_message.Message):
        __slots__ = ("deleted",)
        DELETED_FIELD_NUMBER: _ClassVar[int]
        deleted: bool
        def __init__(self, deleted: _Optional[bool] = ...) -> None: ...
    class DeviceInfo(_message.Message):
        __slots__ = ("manufacturer", "firmware_version", "hardware_version", "serial_number", "mac_address", "vivint_product", "uei_product", "google_product")
        MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
        FIRMWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
        HARDWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
        SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
        MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
        VIVINT_PRODUCT_FIELD_NUMBER: _ClassVar[int]
        UEI_PRODUCT_FIELD_NUMBER: _ClassVar[int]
        GOOGLE_PRODUCT_FIELD_NUMBER: _ClassVar[int]
        manufacturer: int
        firmware_version: str
        hardware_version: str
        serial_number: str
        mac_address: str
        vivint_product: int
        uei_product: int
        google_product: int
        def __init__(self, manufacturer: _Optional[int] = ..., firmware_version: _Optional[str] = ..., hardware_version: _Optional[str] = ..., serial_number: _Optional[str] = ..., mac_address: _Optional[str] = ..., vivint_product: _Optional[int] = ..., uei_product: _Optional[int] = ..., google_product: _Optional[int] = ...) -> None: ...
    class HumidityDetection(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: int
        def __init__(self, value: _Optional[int] = ...) -> None: ...
    class HumiditySetpoint(_message.Message):
        __slots__ = ("setpoint",)
        SETPOINT_FIELD_NUMBER: _ClassVar[int]
        setpoint: int
        def __init__(self, setpoint: _Optional[int] = ...) -> None: ...
    class Online(_message.Message):
        __slots__ = ("value", "offline_reason")
        VALUE_FIELD_NUMBER: _ClassVar[int]
        OFFLINE_REASON_FIELD_NUMBER: _ClassVar[int]
        value: bool
        offline_reason: Component.OfflineReason
        def __init__(self, value: _Optional[bool] = ..., offline_reason: _Optional[_Union[Component.OfflineReason, str]] = ...) -> None: ...
    class Rebootable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Schedule(_message.Message):
        __slots__ = ("weekday_schedule", "weekend_schedule", "schedule_enabled", "schedule_initialized")
        class Period(_message.Message):
            __slots__ = ("wake", "leave", "arrive", "sleep")
            class Stage(_message.Message):
                __slots__ = ("start_time", "heat_setpoint", "cool_setpoint")
                class Time(_message.Message):
                    __slots__ = ("hour", "minute")
                    HOUR_FIELD_NUMBER: _ClassVar[int]
                    MINUTE_FIELD_NUMBER: _ClassVar[int]
                    hour: int
                    minute: int
                    def __init__(self, hour: _Optional[int] = ..., minute: _Optional[int] = ...) -> None: ...
                START_TIME_FIELD_NUMBER: _ClassVar[int]
                HEAT_SETPOINT_FIELD_NUMBER: _ClassVar[int]
                COOL_SETPOINT_FIELD_NUMBER: _ClassVar[int]
                start_time: Component.Schedule.Period.Stage.Time
                heat_setpoint: float
                cool_setpoint: float
                def __init__(self, start_time: _Optional[_Union[Component.Schedule.Period.Stage.Time, _Mapping]] = ..., heat_setpoint: _Optional[float] = ..., cool_setpoint: _Optional[float] = ...) -> None: ...
            WAKE_FIELD_NUMBER: _ClassVar[int]
            LEAVE_FIELD_NUMBER: _ClassVar[int]
            ARRIVE_FIELD_NUMBER: _ClassVar[int]
            SLEEP_FIELD_NUMBER: _ClassVar[int]
            wake: Component.Schedule.Period.Stage
            leave: Component.Schedule.Period.Stage
            arrive: Component.Schedule.Period.Stage
            sleep: Component.Schedule.Period.Stage
            def __init__(self, wake: _Optional[_Union[Component.Schedule.Period.Stage, _Mapping]] = ..., leave: _Optional[_Union[Component.Schedule.Period.Stage, _Mapping]] = ..., arrive: _Optional[_Union[Component.Schedule.Period.Stage, _Mapping]] = ..., sleep: _Optional[_Union[Component.Schedule.Period.Stage, _Mapping]] = ...) -> None: ...
        WEEKDAY_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
        WEEKEND_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
        SCHEDULE_ENABLED_FIELD_NUMBER: _ClassVar[int]
        SCHEDULE_INITIALIZED_FIELD_NUMBER: _ClassVar[int]
        weekday_schedule: Component.Schedule.Period
        weekend_schedule: Component.Schedule.Period
        schedule_enabled: bool
        schedule_initialized: bool
        def __init__(self, weekday_schedule: _Optional[_Union[Component.Schedule.Period, _Mapping]] = ..., weekend_schedule: _Optional[_Union[Component.Schedule.Period, _Mapping]] = ..., schedule_enabled: _Optional[bool] = ..., schedule_initialized: _Optional[bool] = ...) -> None: ...
    class SetpointLock(_message.Message):
        __slots__ = ("enabled", "lower_cool", "lower_heat", "upper_cool", "upper_heat", "max_heat", "min_heat", "max_cool", "min_cool")
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        LOWER_COOL_FIELD_NUMBER: _ClassVar[int]
        LOWER_HEAT_FIELD_NUMBER: _ClassVar[int]
        UPPER_COOL_FIELD_NUMBER: _ClassVar[int]
        UPPER_HEAT_FIELD_NUMBER: _ClassVar[int]
        MAX_HEAT_FIELD_NUMBER: _ClassVar[int]
        MIN_HEAT_FIELD_NUMBER: _ClassVar[int]
        MAX_COOL_FIELD_NUMBER: _ClassVar[int]
        MIN_COOL_FIELD_NUMBER: _ClassVar[int]
        enabled: bool
        lower_cool: float
        lower_heat: float
        upper_cool: float
        upper_heat: float
        max_heat: float
        min_heat: float
        max_cool: float
        min_cool: float
        def __init__(self, enabled: _Optional[bool] = ..., lower_cool: _Optional[float] = ..., lower_heat: _Optional[float] = ..., upper_cool: _Optional[float] = ..., upper_heat: _Optional[float] = ..., max_heat: _Optional[float] = ..., min_heat: _Optional[float] = ..., max_cool: _Optional[float] = ..., min_cool: _Optional[float] = ...) -> None: ...
    class Setpoints(_message.Message):
        __slots__ = ("cool_setpoint", "heat_setpoint", "minimum_temperature", "maximum_temperature", "min_setpoint_difference_c", "min_setpoint_difference_f")
        COOL_SETPOINT_FIELD_NUMBER: _ClassVar[int]
        HEAT_SETPOINT_FIELD_NUMBER: _ClassVar[int]
        MINIMUM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        MAXIMUM_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        MIN_SETPOINT_DIFFERENCE_C_FIELD_NUMBER: _ClassVar[int]
        MIN_SETPOINT_DIFFERENCE_F_FIELD_NUMBER: _ClassVar[int]
        cool_setpoint: float
        heat_setpoint: float
        minimum_temperature: float
        maximum_temperature: float
        min_setpoint_difference_c: float
        min_setpoint_difference_f: float
        def __init__(self, cool_setpoint: _Optional[float] = ..., heat_setpoint: _Optional[float] = ..., minimum_temperature: _Optional[float] = ..., maximum_temperature: _Optional[float] = ..., min_setpoint_difference_c: _Optional[float] = ..., min_setpoint_difference_f: _Optional[float] = ...) -> None: ...
    class SmartComfortTargets(_message.Message):
        __slots__ = ("cool_setpoints", "heat_setpoints")
        class Setpoints(_message.Message):
            __slots__ = ("home", "away", "sleep", "vacation")
            HOME_FIELD_NUMBER: _ClassVar[int]
            AWAY_FIELD_NUMBER: _ClassVar[int]
            SLEEP_FIELD_NUMBER: _ClassVar[int]
            VACATION_FIELD_NUMBER: _ClassVar[int]
            home: float
            away: float
            sleep: float
            vacation: float
            def __init__(self, home: _Optional[float] = ..., away: _Optional[float] = ..., sleep: _Optional[float] = ..., vacation: _Optional[float] = ...) -> None: ...
        COOL_SETPOINTS_FIELD_NUMBER: _ClassVar[int]
        HEAT_SETPOINTS_FIELD_NUMBER: _ClassVar[int]
        cool_setpoints: Component.SmartComfortTargets.Setpoints
        heat_setpoints: Component.SmartComfortTargets.Setpoints
        def __init__(self, cool_setpoints: _Optional[_Union[Component.SmartComfortTargets.Setpoints, _Mapping]] = ..., heat_setpoints: _Optional[_Union[Component.SmartComfortTargets.Setpoints, _Mapping]] = ...) -> None: ...
    class TemperatureDetection(_message.Message):
        __slots__ = ("current_temperature",)
        CURRENT_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        current_temperature: float
        def __init__(self, current_temperature: _Optional[float] = ...) -> None: ...
    class WiFi(_message.Message):
        __slots__ = ("ssid",)
        SSID_FIELD_NUMBER: _ClassVar[int]
        ssid: str
        def __init__(self, ssid: _Optional[str] = ...) -> None: ...
    class ZwaveDiagnostics(_message.Message):
        __slots__ = ("protocol_description",)
        PROTOCOL_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        protocol_description: str
        def __init__(self, protocol_description: _Optional[str] = ...) -> None: ...
    class DemandResponse(_message.Message):
        __slots__ = ("event_id", "active", "start_time", "end_time", "setpoint_target", "event_type", "event_status")
        class EventStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            EVENT_STATUS_UNSPECIFIED: _ClassVar[Component.DemandResponse.EventStatus]
            EVENT_STATUS_NORMAL: _ClassVar[Component.DemandResponse.EventStatus]
            EVENT_STATUS_PRE_CONDITIONING: _ClassVar[Component.DemandResponse.EventStatus]
            EVENT_STATUS_INACTIVE: _ClassVar[Component.DemandResponse.EventStatus]
        EVENT_STATUS_UNSPECIFIED: Component.DemandResponse.EventStatus
        EVENT_STATUS_NORMAL: Component.DemandResponse.EventStatus
        EVENT_STATUS_PRE_CONDITIONING: Component.DemandResponse.EventStatus
        EVENT_STATUS_INACTIVE: Component.DemandResponse.EventStatus
        class SetpointTarget(_message.Message):
            __slots__ = ("target_type", "setpoint")
            class TargetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
                __slots__ = ()
                UNSPECIFIED: _ClassVar[Component.DemandResponse.SetpointTarget.TargetType]
                COOL: _ClassVar[Component.DemandResponse.SetpointTarget.TargetType]
                HEAT: _ClassVar[Component.DemandResponse.SetpointTarget.TargetType]
            UNSPECIFIED: Component.DemandResponse.SetpointTarget.TargetType
            COOL: Component.DemandResponse.SetpointTarget.TargetType
            HEAT: Component.DemandResponse.SetpointTarget.TargetType
            TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
            SETPOINT_FIELD_NUMBER: _ClassVar[int]
            target_type: Component.DemandResponse.SetpointTarget.TargetType
            setpoint: float
            def __init__(self, target_type: _Optional[_Union[Component.DemandResponse.SetpointTarget.TargetType, str]] = ..., setpoint: _Optional[float] = ...) -> None: ...
        EVENT_ID_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_FIELD_NUMBER: _ClassVar[int]
        START_TIME_FIELD_NUMBER: _ClassVar[int]
        END_TIME_FIELD_NUMBER: _ClassVar[int]
        SETPOINT_TARGET_FIELD_NUMBER: _ClassVar[int]
        EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        EVENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        event_id: str
        active: bool
        start_time: _timestamp_pb2.Timestamp
        end_time: _timestamp_pb2.Timestamp
        setpoint_target: Component.DemandResponse.SetpointTarget
        event_type: Component.DemandResponse.EventStatus
        event_status: Component.DemandResponse.EventStatus
        def __init__(self, event_id: _Optional[str] = ..., active: _Optional[bool] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., setpoint_target: _Optional[_Union[Component.DemandResponse.SetpointTarget, _Mapping]] = ..., event_type: _Optional[_Union[Component.DemandResponse.EventStatus, str]] = ..., event_status: _Optional[_Union[Component.DemandResponse.EventStatus, str]] = ...) -> None: ...
    class Battery(_message.Message):
        __slots__ = ("battery_level", "battery_status")
        class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.Battery.Status]
            NORMAL: _ClassVar[Component.Battery.Status]
            LOW: _ClassVar[Component.Battery.Status]
            CRITICAL: _ClassVar[Component.Battery.Status]
        UNSPECIFIED: Component.Battery.Status
        NORMAL: Component.Battery.Status
        LOW: Component.Battery.Status
        CRITICAL: Component.Battery.Status
        BATTERY_LEVEL_FIELD_NUMBER: _ClassVar[int]
        BATTERY_STATUS_FIELD_NUMBER: _ClassVar[int]
        battery_level: int
        battery_status: Component.Battery.Status
        def __init__(self, battery_level: _Optional[int] = ..., battery_status: _Optional[_Union[Component.Battery.Status, str]] = ...) -> None: ...
    class FanSetting(_message.Message):
        __slots__ = ("modes_supported", "current_mode", "is_on")
        class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.FanSetting.Mode]
            FIFTEEN_MINUTE: _ClassVar[Component.FanSetting.Mode]
            THIRTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            FORTY_FIVE_MINUTE: _ClassVar[Component.FanSetting.Mode]
            SIXTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            ONE_TWENTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            TWO_FORTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            FOUR_EIGHTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            SEVEN_TWENTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            NINE_SIXTY_MINUTE: _ClassVar[Component.FanSetting.Mode]
            AUTO_LOW: _ClassVar[Component.FanSetting.Mode]
            AUTO_HIGH: _ClassVar[Component.FanSetting.Mode]
            ON_LOW: _ClassVar[Component.FanSetting.Mode]
            ON_HIGH: _ClassVar[Component.FanSetting.Mode]
        UNSPECIFIED: Component.FanSetting.Mode
        FIFTEEN_MINUTE: Component.FanSetting.Mode
        THIRTY_MINUTE: Component.FanSetting.Mode
        FORTY_FIVE_MINUTE: Component.FanSetting.Mode
        SIXTY_MINUTE: Component.FanSetting.Mode
        ONE_TWENTY_MINUTE: Component.FanSetting.Mode
        TWO_FORTY_MINUTE: Component.FanSetting.Mode
        FOUR_EIGHTY_MINUTE: Component.FanSetting.Mode
        SEVEN_TWENTY_MINUTE: Component.FanSetting.Mode
        NINE_SIXTY_MINUTE: Component.FanSetting.Mode
        AUTO_LOW: Component.FanSetting.Mode
        AUTO_HIGH: Component.FanSetting.Mode
        ON_LOW: Component.FanSetting.Mode
        ON_HIGH: Component.FanSetting.Mode
        MODES_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
        CURRENT_MODE_FIELD_NUMBER: _ClassVar[int]
        IS_ON_FIELD_NUMBER: _ClassVar[int]
        modes_supported: _containers.RepeatedScalarFieldContainer[Component.FanSetting.Mode]
        current_mode: Component.FanSetting.Mode
        is_on: bool
        def __init__(self, modes_supported: _Optional[_Iterable[_Union[Component.FanSetting.Mode, str]]] = ..., current_mode: _Optional[_Union[Component.FanSetting.Mode, str]] = ..., is_on: _Optional[bool] = ...) -> None: ...
    class HoldMode(_message.Message):
        __slots__ = ("mode",)
        class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.HoldMode.Mode]
            BY_SCHEDULE: _ClassVar[Component.HoldMode.Mode]
            UNTIL_NEXT: _ClassVar[Component.HoldMode.Mode]
            TWO_HOURS: _ClassVar[Component.HoldMode.Mode]
            PERMANENT: _ClassVar[Component.HoldMode.Mode]
        UNSPECIFIED: Component.HoldMode.Mode
        BY_SCHEDULE: Component.HoldMode.Mode
        UNTIL_NEXT: Component.HoldMode.Mode
        TWO_HOURS: Component.HoldMode.Mode
        PERMANENT: Component.HoldMode.Mode
        MODE_FIELD_NUMBER: _ClassVar[int]
        mode: Component.HoldMode.Mode
        def __init__(self, mode: _Optional[_Union[Component.HoldMode.Mode, str]] = ...) -> None: ...
    class HumidityMode(_message.Message):
        __slots__ = ("mode", "modes_supported")
        class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.HumidityMode.Mode]
            OFF: _ClassVar[Component.HumidityMode.Mode]
            HUMIDIFY: _ClassVar[Component.HumidityMode.Mode]
            DEHUMIDIFY: _ClassVar[Component.HumidityMode.Mode]
        UNSPECIFIED: Component.HumidityMode.Mode
        OFF: Component.HumidityMode.Mode
        HUMIDIFY: Component.HumidityMode.Mode
        DEHUMIDIFY: Component.HumidityMode.Mode
        MODE_FIELD_NUMBER: _ClassVar[int]
        MODES_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
        mode: Component.HumidityMode.Mode
        modes_supported: _containers.RepeatedScalarFieldContainer[Component.HumidityMode.Mode]
        def __init__(self, mode: _Optional[_Union[Component.HumidityMode.Mode, str]] = ..., modes_supported: _Optional[_Iterable[_Union[Component.HumidityMode.Mode, str]]] = ...) -> None: ...
    class OperatingModeSetting(_message.Message):
        __slots__ = ("modes_supported", "current_mode", "last_active_mode")
        class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.OperatingModeSetting.Mode]
            OFF: _ClassVar[Component.OperatingModeSetting.Mode]
            HEAT: _ClassVar[Component.OperatingModeSetting.Mode]
            COOL: _ClassVar[Component.OperatingModeSetting.Mode]
            AUTO: _ClassVar[Component.OperatingModeSetting.Mode]
            EMERGENCY_HEAT: _ClassVar[Component.OperatingModeSetting.Mode]
            RESUME: _ClassVar[Component.OperatingModeSetting.Mode]
            FAN_ONLY: _ClassVar[Component.OperatingModeSetting.Mode]
            FURNACE: _ClassVar[Component.OperatingModeSetting.Mode]
            DRY_AIR: _ClassVar[Component.OperatingModeSetting.Mode]
            MOIST_AIR: _ClassVar[Component.OperatingModeSetting.Mode]
            AUTO_CHANGEOVER: _ClassVar[Component.OperatingModeSetting.Mode]
            ENERGY_SAVE_HEAT: _ClassVar[Component.OperatingModeSetting.Mode]
            ENERGY_SAVE_COOL: _ClassVar[Component.OperatingModeSetting.Mode]
            AWAY: _ClassVar[Component.OperatingModeSetting.Mode]
            ECO: _ClassVar[Component.OperatingModeSetting.Mode]
        UNSPECIFIED: Component.OperatingModeSetting.Mode
        OFF: Component.OperatingModeSetting.Mode
        HEAT: Component.OperatingModeSetting.Mode
        COOL: Component.OperatingModeSetting.Mode
        AUTO: Component.OperatingModeSetting.Mode
        EMERGENCY_HEAT: Component.OperatingModeSetting.Mode
        RESUME: Component.OperatingModeSetting.Mode
        FAN_ONLY: Component.OperatingModeSetting.Mode
        FURNACE: Component.OperatingModeSetting.Mode
        DRY_AIR: Component.OperatingModeSetting.Mode
        MOIST_AIR: Component.OperatingModeSetting.Mode
        AUTO_CHANGEOVER: Component.OperatingModeSetting.Mode
        ENERGY_SAVE_HEAT: Component.OperatingModeSetting.Mode
        ENERGY_SAVE_COOL: Component.OperatingModeSetting.Mode
        AWAY: Component.OperatingModeSetting.Mode
        ECO: Component.OperatingModeSetting.Mode
        MODES_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
        CURRENT_MODE_FIELD_NUMBER: _ClassVar[int]
        LAST_ACTIVE_MODE_FIELD_NUMBER: _ClassVar[int]
        modes_supported: _containers.RepeatedScalarFieldContainer[Component.OperatingModeSetting.Mode]
        current_mode: Component.OperatingModeSetting.Mode
        last_active_mode: Component.OperatingModeSetting.Mode
        def __init__(self, modes_supported: _Optional[_Iterable[_Union[Component.OperatingModeSetting.Mode, str]]] = ..., current_mode: _Optional[_Union[Component.OperatingModeSetting.Mode, str]] = ..., last_active_mode: _Optional[_Union[Component.OperatingModeSetting.Mode, str]] = ...) -> None: ...
    class OperatingState(_message.Message):
        __slots__ = ("current_state", "last_active_state")
        class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNSPECIFIED: _ClassVar[Component.OperatingState.State]
            IDLE: _ClassVar[Component.OperatingState.State]
            HEATING: _ClassVar[Component.OperatingState.State]
            COOLING: _ClassVar[Component.OperatingState.State]
            FAN_ON: _ClassVar[Component.OperatingState.State]
            ERROR: _ClassVar[Component.OperatingState.State]
        UNSPECIFIED: Component.OperatingState.State
        IDLE: Component.OperatingState.State
        HEATING: Component.OperatingState.State
        COOLING: Component.OperatingState.State
        FAN_ON: Component.OperatingState.State
        ERROR: Component.OperatingState.State
        CURRENT_STATE_FIELD_NUMBER: _ClassVar[int]
        LAST_ACTIVE_STATE_FIELD_NUMBER: _ClassVar[int]
        current_state: Component.OperatingState.State
        last_active_state: Component.OperatingState.State
        def __init__(self, current_state: _Optional[_Union[Component.OperatingState.State, str]] = ..., last_active_state: _Optional[_Union[Component.OperatingState.State, str]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_DETECTION_FIELD_NUMBER: _ClassVar[int]
    SETPOINTS_FIELD_NUMBER: _ClassVar[int]
    FAN_SETTING_FIELD_NUMBER: _ClassVar[int]
    ZWAVE_DIAGNOSTICS_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_DETECTION_FIELD_NUMBER: _ClassVar[int]
    SETPOINT_LOCK_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_SETTING_FIELD_NUMBER: _ClassVar[int]
    OPERATING_STATE_FIELD_NUMBER: _ClassVar[int]
    BATTERY_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_MODE_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    DELETABLE_FIELD_NUMBER: _ClassVar[int]
    REBOOTABLE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_INFO_FIELD_NUMBER: _ClassVar[int]
    HOLD_MODE_FIELD_NUMBER: _ClassVar[int]
    DEMAND_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SMART_COMFORT_TARGETS_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    WI_FI_FIELD_NUMBER: _ClassVar[int]
    id: str
    temperature_detection: Component.TemperatureDetection
    setpoints: Component.Setpoints
    fan_setting: Component.FanSetting
    zwave_diagnostics: Component.ZwaveDiagnostics
    humidity_detection: Component.HumidityDetection
    setpoint_lock: Component.SetpointLock
    schedule: Component.Schedule
    operating_mode_setting: Component.OperatingModeSetting
    operating_state: Component.OperatingState
    battery: Component.Battery
    humidity_mode: Component.HumidityMode
    humidity_setpoint: Component.HumiditySetpoint
    deletable: Component.Deletable
    rebootable: Component.Rebootable
    device_info: Component.DeviceInfo
    hold_mode: Component.HoldMode
    demand_response: Component.DemandResponse
    smart_comfort_targets: Component.SmartComfortTargets
    online: Component.Online
    wi_fi: Component.WiFi
    def __init__(self, id: _Optional[str] = ..., temperature_detection: _Optional[_Union[Component.TemperatureDetection, _Mapping]] = ..., setpoints: _Optional[_Union[Component.Setpoints, _Mapping]] = ..., fan_setting: _Optional[_Union[Component.FanSetting, _Mapping]] = ..., zwave_diagnostics: _Optional[_Union[Component.ZwaveDiagnostics, _Mapping]] = ..., humidity_detection: _Optional[_Union[Component.HumidityDetection, _Mapping]] = ..., setpoint_lock: _Optional[_Union[Component.SetpointLock, _Mapping]] = ..., schedule: _Optional[_Union[Component.Schedule, _Mapping]] = ..., operating_mode_setting: _Optional[_Union[Component.OperatingModeSetting, _Mapping]] = ..., operating_state: _Optional[_Union[Component.OperatingState, _Mapping]] = ..., battery: _Optional[_Union[Component.Battery, _Mapping]] = ..., humidity_mode: _Optional[_Union[Component.HumidityMode, _Mapping]] = ..., humidity_setpoint: _Optional[_Union[Component.HumiditySetpoint, _Mapping]] = ..., deletable: _Optional[_Union[Component.Deletable, _Mapping]] = ..., rebootable: _Optional[_Union[Component.Rebootable, _Mapping]] = ..., device_info: _Optional[_Union[Component.DeviceInfo, _Mapping]] = ..., hold_mode: _Optional[_Union[Component.HoldMode, _Mapping]] = ..., demand_response: _Optional[_Union[Component.DemandResponse, _Mapping]] = ..., smart_comfort_targets: _Optional[_Union[Component.SmartComfortTargets, _Mapping]] = ..., online: _Optional[_Union[Component.Online, _Mapping]] = ..., wi_fi: _Optional[_Union[Component.WiFi, _Mapping]] = ...) -> None: ...

class Ct100ThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Ct200ThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteDeviceRequest(_message.Message):
    __slots__ = ("system_id", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class DeleteDeviceResponse(_message.Message):
    __slots__ = ("success", "failure")
    class Failure(_message.Message):
        __slots__ = ("reason", "message")
        REASON_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        reason: int
        message: str
        def __init__(self, reason: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
    class Success(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    success: DeleteDeviceResponse.Success
    failure: DeleteDeviceResponse.Failure
    def __init__(self, success: _Optional[_Union[DeleteDeviceResponse.Success, _Mapping]] = ..., failure: _Optional[_Union[DeleteDeviceResponse.Failure, _Mapping]] = ...) -> None: ...

class DemandResponseEasyEnrollmentRequest(_message.Message):
    __slots__ = ("system_id", "retail_electric_provider", "platform_source")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    RETAIL_ELECTRIC_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_SOURCE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    retail_electric_provider: RetailElectricProvider
    platform_source: int
    def __init__(self, system_id: _Optional[int] = ..., retail_electric_provider: _Optional[_Union[RetailElectricProvider, str]] = ..., platform_source: _Optional[int] = ...) -> None: ...

class DemandResponseEasyEnrollmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DemandResponseEnrollmentRequest(_message.Message):
    __slots__ = ("system_id", "retail_electric_provider", "utility_account_number", "platform_source")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    RETAIL_ELECTRIC_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    UTILITY_ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_SOURCE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    retail_electric_provider: RetailElectricProvider
    utility_account_number: str
    platform_source: int
    def __init__(self, system_id: _Optional[int] = ..., retail_electric_provider: _Optional[_Union[RetailElectricProvider, str]] = ..., utility_account_number: _Optional[str] = ..., platform_source: _Optional[int] = ...) -> None: ...

class DemandResponseEnrollmentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DemandResponseOptOutRequest(_message.Message):
    __slots__ = ("system_id", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class DemandResponseOptOutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DismissAnomalyAlertRequest(_message.Message):
    __slots__ = ("system_id", "vendor_device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    vendor_device_id: str
    def __init__(self, system_id: _Optional[int] = ..., vendor_device_id: _Optional[str] = ...) -> None: ...

class DismissAnomalyAlertResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Ev2ThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Ev2ZThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAccountInfoRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetAccountInfoResponse(_message.Message):
    __slots__ = ("system_id", "features", "services")
    class FeaturesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bool] = ...) -> None: ...
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    features: _containers.ScalarMap[str, bool]
    services: _containers.RepeatedCompositeFieldContainer[ServiceFieldMessage]
    def __init__(self, system_id: _Optional[int] = ..., features: _Optional[_Mapping[str, bool]] = ..., services: _Optional[_Iterable[_Union[ServiceFieldMessage, _Mapping]]] = ...) -> None: ...

class GetAnomaliesRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetAnomaliesResponse(_message.Message):
    __slots__ = ("anomalies",)
    ANOMALIES_FIELD_NUMBER: _ClassVar[int]
    anomalies: _containers.RepeatedCompositeFieldContainer[Anomaly]
    def __init__(self, anomalies: _Optional[_Iterable[_Union[Anomaly, _Mapping]]] = ...) -> None: ...

class GetClimateDevicesRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetClimateDevicesResponse(_message.Message):
    __slots__ = ("climate_devices",)
    CLIMATE_DEVICES_FIELD_NUMBER: _ClassVar[int]
    climate_devices: _containers.RepeatedCompositeFieldContainer[ClimateDevice]
    def __init__(self, climate_devices: _Optional[_Iterable[_Union[ClimateDevice, _Mapping]]] = ...) -> None: ...

class GetClimateDevicesStreamingRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetClimateDevicesStreamingResponse(_message.Message):
    __slots__ = ("climate_devices", "deleted_device_ids")
    CLIMATE_DEVICES_FIELD_NUMBER: _ClassVar[int]
    DELETED_DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    climate_devices: _containers.RepeatedCompositeFieldContainer[ClimateDevice]
    deleted_device_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, climate_devices: _Optional[_Iterable[_Union[ClimateDevice, _Mapping]]] = ..., deleted_device_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetGlobalSettingsRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetGlobalSettingsResponse(_message.Message):
    __slots__ = ("temperature_units",)
    class TemperatureUnits(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[GetGlobalSettingsResponse.TemperatureUnits]
        CELSIUS: _ClassVar[GetGlobalSettingsResponse.TemperatureUnits]
        FAHRENHEIT: _ClassVar[GetGlobalSettingsResponse.TemperatureUnits]
    UNSPECIFIED: GetGlobalSettingsResponse.TemperatureUnits
    CELSIUS: GetGlobalSettingsResponse.TemperatureUnits
    FAHRENHEIT: GetGlobalSettingsResponse.TemperatureUnits
    TEMPERATURE_UNITS_FIELD_NUMBER: _ClassVar[int]
    temperature_units: GetGlobalSettingsResponse.TemperatureUnits
    def __init__(self, temperature_units: _Optional[_Union[GetGlobalSettingsResponse.TemperatureUnits, str]] = ...) -> None: ...

class GetHVACFilterRequest(_message.Message):
    __slots__ = ("system_id", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class GetHVACFilterResponse(_message.Message):
    __slots__ = ("filter",)
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter: HVACFilter
    def __init__(self, filter: _Optional[_Union[HVACFilter, _Mapping]] = ...) -> None: ...

class GetSmartComfortEnabledRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetSmartComfortEnabledResponse(_message.Message):
    __slots__ = ("is_smart_comfort_enabled",)
    IS_SMART_COMFORT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    is_smart_comfort_enabled: bool
    def __init__(self, is_smart_comfort_enabled: _Optional[bool] = ...) -> None: ...

class GetSmartComfortOnboardingStatusRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetSmartComfortOnboardingStatusResponse(_message.Message):
    __slots__ = ("is_onboarding_completed",)
    IS_ONBOARDING_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    is_onboarding_completed: bool
    def __init__(self, is_onboarding_completed: _Optional[bool] = ...) -> None: ...

class GetSmartComfortStateRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetSmartComfortStateResponse(_message.Message):
    __slots__ = ("vacancy_state",)
    VACANCY_STATE_FIELD_NUMBER: _ClassVar[int]
    vacancy_state: Component.OperatingState.State
    def __init__(self, vacancy_state: _Optional[_Union[Component.OperatingState.State, str]] = ...) -> None: ...

class GetTechnicianDispatchEligibilityRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetTechnicianDispatchEligibilityResponse(_message.Message):
    __slots__ = ("eligible",)
    ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    eligible: bool
    def __init__(self, eligible: _Optional[bool] = ...) -> None: ...

class GetTimeZoneRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetTimeZoneResponse(_message.Message):
    __slots__ = ("timezone",)
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timezone: TimeZones
    def __init__(self, timezone: _Optional[_Union[TimeZones, str]] = ...) -> None: ...

class HVACFilter(_message.Message):
    __slots__ = ("system_id", "device_id", "reminder_sensitivity", "needs_replacement", "last_replaced", "snoozed_until", "initial_filter_response", "reminders_enabled", "snoozed_until_days")
    class InitialFilterResponse(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INITIAL_FILTER_RESPONSE_UNSPECIFIED: _ClassVar[HVACFilter.InitialFilterResponse]
        INITIAL_FILTER_RESPONSE_YES: _ClassVar[HVACFilter.InitialFilterResponse]
        INITIAL_FILTER_RESPONSE_NO: _ClassVar[HVACFilter.InitialFilterResponse]
        INITIAL_FILTER_RESPONSE_DONT_REMEMBER: _ClassVar[HVACFilter.InitialFilterResponse]
    INITIAL_FILTER_RESPONSE_UNSPECIFIED: HVACFilter.InitialFilterResponse
    INITIAL_FILTER_RESPONSE_YES: HVACFilter.InitialFilterResponse
    INITIAL_FILTER_RESPONSE_NO: HVACFilter.InitialFilterResponse
    INITIAL_FILTER_RESPONSE_DONT_REMEMBER: HVACFilter.InitialFilterResponse
    class ReminderSensitivity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REMINDER_SENSITIVITY_UNSPECIFIED: _ClassVar[HVACFilter.ReminderSensitivity]
        REMINDER_SENSITIVITY_STANDARD: _ClassVar[HVACFilter.ReminderSensitivity]
        REMINDER_SENSITIVITY_HIGH: _ClassVar[HVACFilter.ReminderSensitivity]
    REMINDER_SENSITIVITY_UNSPECIFIED: HVACFilter.ReminderSensitivity
    REMINDER_SENSITIVITY_STANDARD: HVACFilter.ReminderSensitivity
    REMINDER_SENSITIVITY_HIGH: HVACFilter.ReminderSensitivity
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    REMINDER_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    NEEDS_REPLACEMENT_FIELD_NUMBER: _ClassVar[int]
    LAST_REPLACED_FIELD_NUMBER: _ClassVar[int]
    SNOOZED_UNTIL_FIELD_NUMBER: _ClassVar[int]
    INITIAL_FILTER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REMINDERS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SNOOZED_UNTIL_DAYS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    reminder_sensitivity: HVACFilter.ReminderSensitivity
    needs_replacement: bool
    last_replaced: _timestamp_pb2.Timestamp
    snoozed_until: _timestamp_pb2.Timestamp
    initial_filter_response: HVACFilter.InitialFilterResponse
    reminders_enabled: bool
    snoozed_until_days: int
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., reminder_sensitivity: _Optional[_Union[HVACFilter.ReminderSensitivity, str]] = ..., needs_replacement: _Optional[bool] = ..., last_replaced: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., snoozed_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., initial_filter_response: _Optional[_Union[HVACFilter.InitialFilterResponse, str]] = ..., reminders_enabled: _Optional[bool] = ..., snoozed_until_days: _Optional[int] = ...) -> None: ...

class IsSmartComfortEligibleRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class IsSmartComfortEligibleResponse(_message.Message):
    __slots__ = ("is_smart_comfort_eligible",)
    IS_SMART_COMFORT_ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    is_smart_comfort_eligible: bool
    def __init__(self, is_smart_comfort_eligible: _Optional[bool] = ...) -> None: ...

class NestThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PairThermostatRequest(_message.Message):
    __slots__ = ("system_id", "existingdeviceids")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    EXISTINGDEVICEIDS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    existingdeviceids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, system_id: _Optional[int] = ..., existingdeviceids: _Optional[_Iterable[str]] = ...) -> None: ...

class PairThermostatResponse(_message.Message):
    __slots__ = ("climate_device",)
    CLIMATE_DEVICE_FIELD_NUMBER: _ClassVar[int]
    climate_device: ClimateDevice
    def __init__(self, climate_device: _Optional[_Union[ClimateDevice, _Mapping]] = ...) -> None: ...

class PegasusThermostatDevice(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RebootThermostatRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ...) -> None: ...

class RebootThermostatResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ServiceFieldMessage(_message.Message):
    __slots__ = ("external_id", "type", "disconnected")
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    external_id: str
    type: str
    disconnected: bool
    def __init__(self, external_id: _Optional[str] = ..., type: _Optional[str] = ..., disconnected: _Optional[bool] = ...) -> None: ...

class SetCoolSetpointRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "fahrenheit", "celsius")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAHRENHEIT_FIELD_NUMBER: _ClassVar[int]
    CELSIUS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    fahrenheit: float
    celsius: float
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., fahrenheit: _Optional[float] = ..., celsius: _Optional[float] = ...) -> None: ...

class SetCoolSetpointResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetEnableFilterReminderRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "enabled")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    enabled: bool
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., enabled: _Optional[bool] = ...) -> None: ...

class SetEnableFilterReminderResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetEnableSetpointLockRequest(_message.Message):
    __slots__ = ("system_id", "enabled", "device_id", "apply_to_all_thermostats")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLY_TO_ALL_THERMOSTATS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    enabled: bool
    device_id: str
    apply_to_all_thermostats: bool
    def __init__(self, system_id: _Optional[int] = ..., enabled: _Optional[bool] = ..., device_id: _Optional[str] = ..., apply_to_all_thermostats: _Optional[bool] = ...) -> None: ...

class SetEnableSetpointLockResponse(_message.Message):
    __slots__ = ("thermostats",)
    class Thermostat(_message.Message):
        __slots__ = ("device_id", "setpoints_auto_adjusted")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        SETPOINTS_AUTO_ADJUSTED_FIELD_NUMBER: _ClassVar[int]
        device_id: str
        setpoints_auto_adjusted: bool
        def __init__(self, device_id: _Optional[str] = ..., setpoints_auto_adjusted: _Optional[bool] = ...) -> None: ...
    THERMOSTATS_FIELD_NUMBER: _ClassVar[int]
    thermostats: _containers.RepeatedCompositeFieldContainer[SetEnableSetpointLockResponse.Thermostat]
    def __init__(self, thermostats: _Optional[_Iterable[_Union[SetEnableSetpointLockResponse.Thermostat, _Mapping]]] = ...) -> None: ...

class SetFanModeRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "mode", "component_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    mode: Component.FanSetting.Mode
    component_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., mode: _Optional[_Union[Component.FanSetting.Mode, str]] = ..., component_id: _Optional[str] = ...) -> None: ...

class SetFanModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetFilterReminderLevelRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "reminder_sensitivity")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    REMINDER_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    reminder_sensitivity: HVACFilter.ReminderSensitivity
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., reminder_sensitivity: _Optional[_Union[HVACFilter.ReminderSensitivity, str]] = ...) -> None: ...

class SetFilterReminderLevelResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetGlobalSettingsRequest(_message.Message):
    __slots__ = ("system_id", "temperature_units")
    class TemperatureUnits(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[SetGlobalSettingsRequest.TemperatureUnits]
        CELSIUS: _ClassVar[SetGlobalSettingsRequest.TemperatureUnits]
        FAHRENHEIT: _ClassVar[SetGlobalSettingsRequest.TemperatureUnits]
    UNSPECIFIED: SetGlobalSettingsRequest.TemperatureUnits
    CELSIUS: SetGlobalSettingsRequest.TemperatureUnits
    FAHRENHEIT: SetGlobalSettingsRequest.TemperatureUnits
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_UNITS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    temperature_units: SetGlobalSettingsRequest.TemperatureUnits
    def __init__(self, system_id: _Optional[int] = ..., temperature_units: _Optional[_Union[SetGlobalSettingsRequest.TemperatureUnits, str]] = ...) -> None: ...

class SetGlobalSettingsResponse(_message.Message):
    __slots__ = ("temperature_units",)
    TEMPERATURE_UNITS_FIELD_NUMBER: _ClassVar[int]
    temperature_units: GetGlobalSettingsResponse.TemperatureUnits
    def __init__(self, temperature_units: _Optional[_Union[GetGlobalSettingsResponse.TemperatureUnits, str]] = ...) -> None: ...

class SetHVACFilterReminderSnoozedRequest(_message.Message):
    __slots__ = ("system_id", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class SetHVACFilterReminderSnoozedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHVACFilterReplacedRequest(_message.Message):
    __slots__ = ("system_id", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class SetHVACFilterReplacedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHeatSetpointRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "fahrenheit", "celsius")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAHRENHEIT_FIELD_NUMBER: _ClassVar[int]
    CELSIUS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    fahrenheit: float
    celsius: float
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., fahrenheit: _Optional[float] = ..., celsius: _Optional[float] = ...) -> None: ...

class SetHeatSetpointResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHoldModeRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "mode", "component_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    mode: Component.HoldMode.Mode
    component_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., mode: _Optional[_Union[Component.HoldMode.Mode, str]] = ..., component_id: _Optional[str] = ...) -> None: ...

class SetHoldModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHumidityModeRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "mode")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    mode: Component.HumidityMode.Mode
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., mode: _Optional[_Union[Component.HumidityMode.Mode, str]] = ...) -> None: ...

class SetHumidityModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHumiditySetpointRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "percentage")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    percentage: int
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., percentage: _Optional[int] = ...) -> None: ...

class SetHumiditySetpointResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetInitialFilterReplacementStatusRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "initial_filter_response")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_FILTER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    initial_filter_response: HVACFilter.InitialFilterResponse
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., initial_filter_response: _Optional[_Union[HVACFilter.InitialFilterResponse, str]] = ...) -> None: ...

class SetInitialFilterReplacementStatusResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetNameRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "name", "component_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    name: str
    component_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., name: _Optional[str] = ..., component_id: _Optional[str] = ...) -> None: ...

class SetNameResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetOperatingModeRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "mode", "component_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    mode: Component.OperatingModeSetting.Mode
    component_id: str
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., mode: _Optional[_Union[Component.OperatingModeSetting.Mode, str]] = ..., component_id: _Optional[str] = ...) -> None: ...

class SetOperatingModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetScheduleEnabledRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "enabled")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    enabled: bool
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., enabled: _Optional[bool] = ...) -> None: ...

class SetScheduleEnabledResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetScheduleRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "schedule")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    schedule: Component.Schedule
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., schedule: _Optional[_Union[Component.Schedule, _Mapping]] = ...) -> None: ...

class SetScheduleResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetSetpointLockRangeRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "apply_to_all_thermostats", "celsiusrange", "fahrenheitrange")
    class Celsius(_message.Message):
        __slots__ = ("lower", "upper")
        LOWER_FIELD_NUMBER: _ClassVar[int]
        UPPER_FIELD_NUMBER: _ClassVar[int]
        lower: float
        upper: float
        def __init__(self, lower: _Optional[float] = ..., upper: _Optional[float] = ...) -> None: ...
    class Fahrenheit(_message.Message):
        __slots__ = ("lower", "upper")
        LOWER_FIELD_NUMBER: _ClassVar[int]
        UPPER_FIELD_NUMBER: _ClassVar[int]
        lower: float
        upper: float
        def __init__(self, lower: _Optional[float] = ..., upper: _Optional[float] = ...) -> None: ...
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLY_TO_ALL_THERMOSTATS_FIELD_NUMBER: _ClassVar[int]
    CELSIUSRANGE_FIELD_NUMBER: _ClassVar[int]
    FAHRENHEITRANGE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    apply_to_all_thermostats: bool
    celsiusrange: SetSetpointLockRangeRequest.Celsius
    fahrenheitrange: SetSetpointLockRangeRequest.Fahrenheit
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., apply_to_all_thermostats: _Optional[bool] = ..., celsiusrange: _Optional[_Union[SetSetpointLockRangeRequest.Celsius, _Mapping]] = ..., fahrenheitrange: _Optional[_Union[SetSetpointLockRangeRequest.Fahrenheit, _Mapping]] = ...) -> None: ...

class SetSetpointLockRangeResponse(_message.Message):
    __slots__ = ("thermostats",)
    class Thermostat(_message.Message):
        __slots__ = ("device_id", "setpoints_auto_adjusted")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        SETPOINTS_AUTO_ADJUSTED_FIELD_NUMBER: _ClassVar[int]
        device_id: str
        setpoints_auto_adjusted: bool
        def __init__(self, device_id: _Optional[str] = ..., setpoints_auto_adjusted: _Optional[bool] = ...) -> None: ...
    THERMOSTATS_FIELD_NUMBER: _ClassVar[int]
    thermostats: _containers.RepeatedCompositeFieldContainer[SetSetpointLockRangeResponse.Thermostat]
    def __init__(self, thermostats: _Optional[_Iterable[_Union[SetSetpointLockRangeResponse.Thermostat, _Mapping]]] = ...) -> None: ...

class SetSmartComfortEnabledRequest(_message.Message):
    __slots__ = ("system_id", "enabled")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    enabled: bool
    def __init__(self, system_id: _Optional[int] = ..., enabled: _Optional[bool] = ...) -> None: ...

class SetSmartComfortEnabledResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetSmartComfortSetpointRequest(_message.Message):
    __slots__ = ("system_id", "state", "cool_setpoint", "heat_setpoint", "device_id")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COOL_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    HEAT_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    state: Component.OperatingState.State
    cool_setpoint: float
    heat_setpoint: float
    device_id: str
    def __init__(self, system_id: _Optional[int] = ..., state: _Optional[_Union[Component.OperatingState.State, str]] = ..., cool_setpoint: _Optional[float] = ..., heat_setpoint: _Optional[float] = ..., device_id: _Optional[str] = ...) -> None: ...

class SetSmartComfortSetpointResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetSmartComfortStateRequest(_message.Message):
    __slots__ = ("system_id", "state")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    state: Component.OperatingState.State
    def __init__(self, system_id: _Optional[int] = ..., state: _Optional[_Union[Component.OperatingState.State, str]] = ...) -> None: ...

class SetSmartComfortStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetTemperatureSetpointsRequest(_message.Message):
    __slots__ = ("system_id", "device_id", "component_id", "heat_fahrenheit", "heat_celsius", "cool_fahrenheit", "cool_celsius")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    HEAT_FAHRENHEIT_FIELD_NUMBER: _ClassVar[int]
    HEAT_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    COOL_FAHRENHEIT_FIELD_NUMBER: _ClassVar[int]
    COOL_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    device_id: str
    component_id: str
    heat_fahrenheit: float
    heat_celsius: float
    cool_fahrenheit: float
    cool_celsius: float
    def __init__(self, system_id: _Optional[int] = ..., device_id: _Optional[str] = ..., component_id: _Optional[str] = ..., heat_fahrenheit: _Optional[float] = ..., heat_celsius: _Optional[float] = ..., cool_fahrenheit: _Optional[float] = ..., cool_celsius: _Optional[float] = ...) -> None: ...

class SetTemperatureSetpointsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetTimeZoneRequest(_message.Message):
    __slots__ = ("system_id", "timezone")
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    timezone: TimeZones
    def __init__(self, system_id: _Optional[int] = ..., timezone: _Optional[_Union[TimeZones, str]] = ...) -> None: ...

class SetTimeZoneResponse(_message.Message):
    __slots__ = ("timezone",)
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timezone: TimeZones
    def __init__(self, timezone: _Optional[_Union[TimeZones, str]] = ...) -> None: ...

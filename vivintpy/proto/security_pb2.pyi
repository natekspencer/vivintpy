import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SecurityState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SECURITY_STATE_UNSPECIFIED: _ClassVar[SecurityState]
    SECURITY_STATE_DISARMED: _ClassVar[SecurityState]
    SECURITY_STATE_ARMING_AWAY_IN_EXIT_DELAY: _ClassVar[SecurityState]
    SECURITY_STATE_ARMING_STAY_IN_EXIT_DELAY: _ClassVar[SecurityState]
    SECURITY_STATE_ARMED_STAY: _ClassVar[SecurityState]
    SECURITY_STATE_ARMED_AWAY: _ClassVar[SecurityState]
    SECURITY_STATE_ARMED_STAY_IN_ENTRY_DELAY: _ClassVar[SecurityState]
    SECURITY_STATE_ARMED_AWAY_IN_ENTRY_DELAY: _ClassVar[SecurityState]
    SECURITY_STATE_ALARM: _ClassVar[SecurityState]
    SECURITY_STATE_ALARM_FIRE: _ClassVar[SecurityState]
    SECURITY_STATE_DISABLED: _ClassVar[SecurityState]
    SECURITY_STATE_WALK_TEST: _ClassVar[SecurityState]

class AlarmType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALARM_TYPE_UNSPECIFIED: _ClassVar[AlarmType]
    ALARM_TYPE_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_POLICE: _ClassVar[AlarmType]
    ALARM_TYPE_FIRE: _ClassVar[AlarmType]
    ALARM_TYPE_EMERGENCY: _ClassVar[AlarmType]
    ALARM_TYPE_CARBON_MONOXIDE: _ClassVar[AlarmType]
    ALARM_TYPE_EXIT_ERROR: _ClassVar[AlarmType]
    ALARM_TYPE_SILENT_BURGLARY: _ClassVar[AlarmType]
    ALARM_TYPE_TWENTY_FOUR_HOUR_AUDIBLE_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_TWENTY_FOUR_HOUR_AUXILIARY_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_AUXILIARY_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_TWENTY_FOUR_HOUR_FIRE_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_TAMPER_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_APPLICATION_PANIC: _ClassVar[AlarmType]
    ALARM_TYPE_MOVEMENT_ALARM: _ClassVar[AlarmType]
    ALARM_TYPE_APPLICATION_EMERGENCY: _ClassVar[AlarmType]
    ALARM_TYPE_APPLICATION_FIRE: _ClassVar[AlarmType]
SECURITY_STATE_UNSPECIFIED: SecurityState
SECURITY_STATE_DISARMED: SecurityState
SECURITY_STATE_ARMING_AWAY_IN_EXIT_DELAY: SecurityState
SECURITY_STATE_ARMING_STAY_IN_EXIT_DELAY: SecurityState
SECURITY_STATE_ARMED_STAY: SecurityState
SECURITY_STATE_ARMED_AWAY: SecurityState
SECURITY_STATE_ARMED_STAY_IN_ENTRY_DELAY: SecurityState
SECURITY_STATE_ARMED_AWAY_IN_ENTRY_DELAY: SecurityState
SECURITY_STATE_ALARM: SecurityState
SECURITY_STATE_ALARM_FIRE: SecurityState
SECURITY_STATE_DISABLED: SecurityState
SECURITY_STATE_WALK_TEST: SecurityState
ALARM_TYPE_UNSPECIFIED: AlarmType
ALARM_TYPE_ALARM: AlarmType
ALARM_TYPE_POLICE: AlarmType
ALARM_TYPE_FIRE: AlarmType
ALARM_TYPE_EMERGENCY: AlarmType
ALARM_TYPE_CARBON_MONOXIDE: AlarmType
ALARM_TYPE_EXIT_ERROR: AlarmType
ALARM_TYPE_SILENT_BURGLARY: AlarmType
ALARM_TYPE_TWENTY_FOUR_HOUR_AUDIBLE_ALARM: AlarmType
ALARM_TYPE_TWENTY_FOUR_HOUR_AUXILIARY_ALARM: AlarmType
ALARM_TYPE_AUXILIARY_ALARM: AlarmType
ALARM_TYPE_TWENTY_FOUR_HOUR_FIRE_ALARM: AlarmType
ALARM_TYPE_TAMPER_ALARM: AlarmType
ALARM_TYPE_APPLICATION_PANIC: AlarmType
ALARM_TYPE_MOVEMENT_ALARM: AlarmType
ALARM_TYPE_APPLICATION_EMERGENCY: AlarmType
ALARM_TYPE_APPLICATION_FIRE: AlarmType

class ZoneInAlarm(_message.Message):
    __slots__ = ("vendor_device_id", "alarm_type", "time", "device_name")
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ALARM_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    alarm_type: AlarmType
    time: _timestamp_pb2.Timestamp
    device_name: str
    def __init__(self, vendor_device_id: _Optional[str] = ..., alarm_type: _Optional[_Union[AlarmType, str]] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_name: _Optional[str] = ...) -> None: ...

class GetSecurityStateRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetSecurityStateResponse(_message.Message):
    __slots__ = ("vendor_device_id", "security_state", "ready_to_arm", "last_updated", "zones_in_alarm")
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_STATE_FIELD_NUMBER: _ClassVar[int]
    READY_TO_ARM_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    ZONES_IN_ALARM_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    security_state: SecurityState
    ready_to_arm: bool
    last_updated: _timestamp_pb2.Timestamp
    zones_in_alarm: _containers.RepeatedCompositeFieldContainer[ZoneInAlarm]
    def __init__(self, vendor_device_id: _Optional[str] = ..., security_state: _Optional[_Union[SecurityState, str]] = ..., ready_to_arm: bool = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., zones_in_alarm: _Optional[_Iterable[_Union[ZoneInAlarm, _Mapping]]] = ...) -> None: ...

class ArmSecurityRequest(_message.Message):
    __slots__ = ("vendor_device_id", "arm_state", "disable_entry_delay", "force_arm")
    class ArmState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ARM_STATE_UNSPECIFIED: _ClassVar[ArmSecurityRequest.ArmState]
        ARM_STATE_ARMED_STAY: _ClassVar[ArmSecurityRequest.ArmState]
        ARM_STATE_ARMED_AWAY: _ClassVar[ArmSecurityRequest.ArmState]
    ARM_STATE_UNSPECIFIED: ArmSecurityRequest.ArmState
    ARM_STATE_ARMED_STAY: ArmSecurityRequest.ArmState
    ARM_STATE_ARMED_AWAY: ArmSecurityRequest.ArmState
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ARM_STATE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ENTRY_DELAY_FIELD_NUMBER: _ClassVar[int]
    FORCE_ARM_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    arm_state: ArmSecurityRequest.ArmState
    disable_entry_delay: bool
    force_arm: bool
    def __init__(self, vendor_device_id: _Optional[str] = ..., arm_state: _Optional[_Union[ArmSecurityRequest.ArmState, str]] = ..., disable_entry_delay: bool = ..., force_arm: bool = ...) -> None: ...

class ArmSecurityResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class DisarmSecurityRequest(_message.Message):
    __slots__ = ("vendor_device_id",)
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    def __init__(self, vendor_device_id: _Optional[str] = ...) -> None: ...

class DisarmSecurityResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class TriggerAlarmRequest(_message.Message):
    __slots__ = ("vendor_device_id", "alarm_state")
    class AlarmState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALARM_STATE_UNSPECIFIED: _ClassVar[TriggerAlarmRequest.AlarmState]
        ALARM_STATE_ALARM_PANIC: _ClassVar[TriggerAlarmRequest.AlarmState]
        ALARM_STATE_ALARM_FIRE: _ClassVar[TriggerAlarmRequest.AlarmState]
        ALARM_STATE_ALARM_EMERGENCY: _ClassVar[TriggerAlarmRequest.AlarmState]
    ALARM_STATE_UNSPECIFIED: TriggerAlarmRequest.AlarmState
    ALARM_STATE_ALARM_PANIC: TriggerAlarmRequest.AlarmState
    ALARM_STATE_ALARM_FIRE: TriggerAlarmRequest.AlarmState
    ALARM_STATE_ALARM_EMERGENCY: TriggerAlarmRequest.AlarmState
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ALARM_STATE_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    alarm_state: TriggerAlarmRequest.AlarmState
    def __init__(self, vendor_device_id: _Optional[str] = ..., alarm_state: _Optional[_Union[TriggerAlarmRequest.AlarmState, str]] = ...) -> None: ...

class TriggerAlarmResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

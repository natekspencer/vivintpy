from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GarageDoorState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GARAGE_DOOR_STATE_UNSPECIFIED: _ClassVar[GarageDoorState]
    GARAGE_DOOR_STATE_CLOSED: _ClassVar[GarageDoorState]
    GARAGE_DOOR_STATE_CLOSING: _ClassVar[GarageDoorState]
    GARAGE_DOOR_STATE_STOPPED: _ClassVar[GarageDoorState]
    GARAGE_DOOR_STATE_OPENING: _ClassVar[GarageDoorState]
    GARAGE_DOOR_STATE_OPENED: _ClassVar[GarageDoorState]
GARAGE_DOOR_STATE_UNSPECIFIED: GarageDoorState
GARAGE_DOOR_STATE_CLOSED: GarageDoorState
GARAGE_DOOR_STATE_CLOSING: GarageDoorState
GARAGE_DOOR_STATE_STOPPED: GarageDoorState
GARAGE_DOOR_STATE_OPENING: GarageDoorState
GARAGE_DOOR_STATE_OPENED: GarageDoorState

class GarageDoorDevice(_message.Message):
    __slots__ = ("vendor_device_id", "name", "state", "online", "cannot_remote_close")
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    CANNOT_REMOTE_CLOSE_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    name: str
    state: GarageDoorState
    online: bool
    cannot_remote_close: bool
    def __init__(self, vendor_device_id: _Optional[str] = ..., name: _Optional[str] = ..., state: _Optional[_Union[GarageDoorState, str]] = ..., online: bool = ..., cannot_remote_close: bool = ...) -> None: ...

class GetAllGarageDoorsRequest(_message.Message):
    __slots__ = ("system_id",)
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    system_id: int
    def __init__(self, system_id: _Optional[int] = ...) -> None: ...

class GetAllGarageDoorsResponse(_message.Message):
    __slots__ = ("garage_doors",)
    GARAGE_DOORS_FIELD_NUMBER: _ClassVar[int]
    garage_doors: _containers.RepeatedCompositeFieldContainer[GarageDoorDevice]
    def __init__(self, garage_doors: _Optional[_Iterable[_Union[GarageDoorDevice, _Mapping]]] = ...) -> None: ...

class OpenGarageDoorRequest(_message.Message):
    __slots__ = ("vendor_device_id",)
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    def __init__(self, vendor_device_id: _Optional[str] = ...) -> None: ...

class OpenGarageDoorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CloseGarageDoorRequest(_message.Message):
    __slots__ = ("vendor_device_id",)
    VENDOR_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_device_id: str
    def __init__(self, vendor_device_id: _Optional[str] = ...) -> None: ...

class CloseGarageDoorResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

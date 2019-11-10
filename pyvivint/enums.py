"""Module that defines varios enums."""


class Enum:

    __names = {}

    @classmethod
    def name(cls, state):
        if not cls.__names:
            cls.__names = {
                value: key
                for key, value in cls.__dict__.items()
                if isinstance(value, int)
            }

        return cls.__names[state]


class VivintDeviceAttributes(Enum):
    """Devine generic vivint device attributes for humans."""
    DeviceType = 't'
    Id = '_id'
    Name = 'n'


class AlarmPanelAttributes(VivintDeviceAttributes):
    """Define alarm panel's attributes for humans."""
    Devices = 'd'
    PanelId = 'panid'
    PartitionId = 'parid'
    State = 's'


class ArmedStates(Enum):
    """Define all possible alarm states."""

    Disarmed = 0
    ArmingAwayInExitDelay = 1
    ArmingStayInExitDelay = 2
    ArmedStay = 3
    ArmedAway = 4
    ArmedStayInEntryDelay = 5
    ArmedAwayInEntryDelay = 6
    Alarm = 7
    AlarmFire = 8
    Disabled = 11
    WalkTest = 12


class CameraAttributes(VivintDeviceAttributes):
    """Define camera's attributes for humans."""

    CameraIPAddress = 'caip'
    CameraPrivacy = 'cpri'
    CameraThumbnailDate = 'ctd'
    CaptureClipOnMotion = 'ccom'
    Online = 'ol'
    WirelessSignalStrenght = 'wiss'


class DoorLockAttributes(VivintDeviceAttributes):
    """Define door lock's attributes for humans."""

    BatteryLevel = 'bl'
    Id = '_id'
    LowBattery = 'lb'
    OperationCount = 'opc'
    OperationFaultCode = 'opfc'
    NodeOnline = 'nonl'
    State = 's'


class DeviceTypes(Enum):
    """Vivint's supported device types."""
    Camera = 'camera_device'
    DoorLock = 'door_lock_device'
    LightModule = 'multilevel_switch_device'
    Thermostat = 'thermostat_device'
    TouchPanel = 'primary_touch_link_device'
    WirelessSensor = 'wireless_sensor'


class WirelessSensorAttributes(VivintDeviceAttributes):
    """Wireless Sensor's attributes for humans."""
    BatteryLevel = 'bl'
    EquipmentCode = 'ec'
    IdBypassed = 'b'
    LowBattery = 'lb'
    SerialNumber = 'ser32'
    State = 's'


class AuthUserAttributes(Enum):
    """AuthUser attributes."""
    IdToken = 'id_token'
    IsReadOnly = 'is_read_only'
    KeepSignedIn = 'keep_signed_in'
    RelayServer = 'rs'
    Users = 'u'

    class UsersAttributes(Enum):
        DocumentSequence = 'DocumentSequence'
        Email = 'e'
        Ghome = 'ghome'
        GroupIds = 'grpid'
        Id = '_id'
        MessageBroadcastChannel = 'mbc'
        Name = 'n'
        PingId = 'pngid'
        RestrictedSystem = 'rsystem'
        SmarthomeSystem = 'smarthomesystem'
        Settings = 'stg'
        System = 'system'
        Timestamp = 'ts'


class PubNumMessageAttributes(Enum):
    Data = 'da'
    Devices = 'd'
    Operation = 'op'
    PanelId = 'panid'
    PartitionId = 'parid'
    Type = 't'

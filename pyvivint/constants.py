"""Module that defines various constants."""


class Constant:

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


class AuthUserAttribute(Constant):
    """AuthUser attributes."""

    ID_TOKEN = "id_token"
    IS_READ_ONLY = "is_read_only"
    KEEP_SIGNED_IN = "keep_signed_in"
    RELAY_SERVER = "rs"
    USERS = "u"


class UserAttribute(Constant):
    """User attributes."""

    DOCUMENT_SEQUENCE = "DocumentSequence"
    EMAIL = "e"
    GHOME = "ghome"
    GROUP_IDS = "grpid"
    ID = "_id"
    MESSAGE_BROADCAST_CHANNEL = "mbc"
    NAME = "n"
    PING_ID = "pngid"
    RESTRICTED_SYSTEM = "rsystem"
    SMART_HOME_SYSTEM = "smarthomesystem"
    SETTINGS = "stg"
    SYSTEM = "system"
    TIMESTAMP = "ts"


class SystemAttribute(Constant):
    """System attributes."""

    PANEL_ID = "panid"
    PARTITION = "par"
    PARTITION_ID = "parid"
    SYSTEM = "system"
    SYSTEM_NICKNAME = "sn"


class PubNubMessageAttribute(Constant):
    """PubNub message attributes."""

    DATA = "da"
    DEVICES = "d"
    OPERATION = "op"
    PANEL_ID = "panid"
    PARTITION_ID = "parid"
    TYPE = "t"


class VivintDeviceAttribute(Constant):
    """Vivint device attributes."""

    BATTERY_LEVEL = "bl"
    CURRENT_SOFTWARE_VERSION = "csv"
    FIRMWARE_VERSION = "fwv"
    ID = "_id"
    LOW_BATTERY = "lb"
    NAME = "n"
    ONLINE = "ol"
    PANEL_ID = "panid"
    SERIAL_NUMBER = "ser"
    SERIAL_NUMBER_32_BIT = "ser32"
    STATE = "s"
    TYPE = "t"


class AlarmPanelAttribute(VivintDeviceAttribute):
    """Alarm panel attributes."""

    DEVICES = "d"
    PARTITION_ID = "parid"


class CameraAttribute(VivintDeviceAttribute):
    """Camera attributes."""

    ACTUAL_TYPE = "act"
    CAMERA_IP_ADDRESS = "caip"
    CAMERA_IP_PORT = "cap"
    CAMERA_MAC = "cmac"
    CAMERA_PRIVACY = "cpri"
    CAMERA_THUMBNAIL_DATE = "ctd"
    CAPTURE_CLIP_ON_MOTION = "ccom"
    SOFTWARE_VERSION = "sv"
    WIRELESS_SIGNAL_STRENGTH = "wiss"


class SwitchAttribute(VivintDeviceAttribute):
    """Switch attributes."""

    VALUE = "val"


class WirelessSensorAttribute(VivintDeviceAttribute):
    """Wireless sensor attributes."""

    BYPASSED = "b"
    EQUIPMENT_CODE = "ec"
    EQUIPMENT_TYPE = "eqt"
    SENSOR_FIRMWARE_VERSION = "sensor_firmware_version"
    SENSOR_TYPE = "set"


class ZWaveDeviceAttribute(VivintDeviceAttribute):
    """ZWave device attributes."""

    OPERATION_COUNT = "opc"
    OPERATION_FAULT_CODE = "opfc"

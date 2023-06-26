"""Module that defines various constants for interacting with the Vivint Sky API."""


class AuthenticationResponse:
    """Authentication response constants."""

    INVALID = "Invalid username and/or password"
    MESSAGE = "msg"
    MFA_REQUIRED = "Multi-factor authentication required"


class MfaVerificationResponse:
    """Multi-factor authentication verification response constants."""

    CODE = "code"
    ERROR = "error"
    MESSAGE = "message"


class AuthUserAttribute:
    """AuthUser attributes."""

    ID_TOKEN = "id_token"
    IS_READ_ONLY = "is_read_only"
    KEEP_SIGNED_IN = "keep_signed_in"
    RELAY_SERVER = "rs"
    USERS = "u"


class UserAttribute:
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


class PanelCredentialAttribute:
    """Panel credential attributes."""

    NAME = "n"
    PASSWORD = "pswd"


class PanelUpdateAttribute:
    """Panel update attributes."""

    AVAILABLE = "av"
    AVAILABLE_VERSION = "asv"
    CURRENT_VERSION = "csv"
    UPDATE_REASON = "rsn"


class SystemAttribute:
    """System attributes."""

    ADMIN = "ad"
    PANEL_ID = "panid"
    PARTITION = "par"
    PARTITION_ID = "parid"
    SYSTEM = "system"
    SYSTEM_NICKNAME = "sn"


class PubNubMessageAttribute:
    """PubNub message attributes."""

    DATA = "da"
    DEVICES = "d"
    OPERATION = "op"
    PANEL_ID = "panid"
    PARTITION_ID = "parid"
    TYPE = "t"


class PubNubOperatorAttribute:
    """PubNub operator attributes."""

    CREATE = "c"
    DELETE = "d"
    UPDATE = "u"
    UPDATE_ALL = "ua"


class VivintDeviceAttribute:
    """Vivint device attributes."""

    BATTERY_LEVEL = "bl"
    BYPASSED = "b"
    CAPABILITY = "ca"
    CAPABILITY_CATEGORY = "caca"
    CURRENT_SOFTWARE_VERSION = "csv"
    FEATURES = "fea"
    FIRMWARE_VERSION = "fwv"
    HIDDEN = "hidden"
    ID = "_id"
    LOW_BATTERY = "lb"
    NAME = "n"
    ONLINE = "ol"
    PANEL_ID = "panid"
    SERIAL_NUMBER = "ser"
    SERIAL_NUMBER_32_BIT = "ser32"
    STATE = "s"
    TAMPER = "ta"
    TYPE = "t"


class AlarmPanelAttribute(VivintDeviceAttribute):
    """Alarm panel attributes."""

    DEVICES = "d"
    MAC_ADDRESS = "pmac"
    PARTITION_ID = "parid"
    UNREGISTERED = "ureg"


class CameraAttribute(VivintDeviceAttribute):
    """Camera attributes."""

    ACTUAL_TYPE = "act"
    CAMERA_DIRECT_AVAILABLE = "cda"
    CAMERA_DIRECT_STREAM_PATH = "cdp"
    CAMERA_DIRECT_STREAM_PATH_STANDARD = "cdps"
    CAMERA_EXTEND_CHIME_ENABLED = "cex"
    CAMERA_IP_ADDRESS = "caip"
    CAMERA_IP_PORT = "cap"
    CAMERA_MAC = "cmac"
    CAMERA_PRIVACY = "cpri"
    CAMERA_THUMBNAIL_DATE = "ctd"
    CAPTURE_CLIP_ON_MOTION = "ccom"
    DETER_ON_DUTY = "deter_on_duty"
    DING_DONG = "dng"
    PASSWORD = "pswd"
    SOFTWARE_VERSION = "sv"
    USERNAME = "un"
    VISITOR_DETECTED = "vdt"
    WIRELESS_SIGNAL_STRENGTH = "wiss"


class SwitchAttribute(VivintDeviceAttribute):
    """Switch attributes."""

    VALUE = "val"


class ThermostatAttribute(VivintDeviceAttribute):
    """Thermostat attributes."""

    ACTUAL_TYPE = "act"
    AUTO_SET_POINTS = "auto"
    AWAY_STATE = "awst"
    COOL_SET_POINT = "csp"
    CURRENT_TEMPERATURE = "val"
    DEHUMIDIFIER_SET_POINT = "dhmdrsp"
    FAN_MODE = "fm"
    FAN_STATE = "fs"
    HEAT_SET_POINT = "hsp"
    HOLD_MODE = "hm"
    HUMIDIFIER_SET_POINT = "hmdrsp"
    HUMIDITY = "hmdt"
    MAXIMUM_TEMPERATURE = "maxt"
    MINIMUM_TEMPERATURE = "mint"
    OPERATING_MODE = "om"
    OPERATING_STATE = "os"
    WEEKDAY_COOL_SCHEDULE = "wdcs"
    WEEKDAY_HEAT_SCHEDULE = "wdhs"
    WEEKEND_COOL_SCHEDULE = "wecs"
    WEEKEND_HEAT_SCHEDULE = "wehs"
    SMART_COMFORT_COOL_TARGET = "scct"
    SMART_COMFORT_HEAT_TARGET = "scht"


class WirelessSensorAttribute(VivintDeviceAttribute):
    """Wireless sensor attributes."""

    EQUIPMENT_CODE = "ec"
    EQUIPMENT_TYPE = "eqt"
    SENSOR_FIRMWARE_VERSION = "sensor_firmware_version"
    SENSOR_TYPE = "set"


class ZWaveDeviceAttribute(VivintDeviceAttribute):
    """Z-Wave device attributes."""

    OPERATION_COUNT = "opc"
    OPERATION_FAULT_CODE = "opfc"

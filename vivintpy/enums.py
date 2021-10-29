"""Module that defines various enums."""
from enum import Enum, IntEnum, unique


@unique
class ArmedState(IntEnum):
    """Armed state."""

    DISARMED = 0
    ARMING_AWAY_IN_EXIT_DELAY = 1
    ARMING_STAY_IN_EXIT_DELAY = 2
    ARMED_STAY = 3
    ARMED_AWAY = 4
    ARMED_STAY_IN_ENTRY_DELAY = 5
    ARMED_AWAY_IN_ENTRY_DELAY = 6
    ALARM = 7
    ALARM_FIRE = 8
    DISABLED = 11
    WALK_TEST = 12


@unique
class CapabilityCategoryType(IntEnum):
    """Capability category type."""

    CAMERA = 1
    DOORBELL = 2
    SWITCH = 3
    THERMOSTAT = 4
    ZWAVE = 5
    TOUCHLINK = 6
    DOOR_LOCK = 7
    MOBILE_BLACKLIST = 8
    GARAGE_DOOR = 9

    # Handle unknown/future capability categories
    UNKNOWN = 0

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class CapabilityType(IntEnum):
    """Capability type."""

    ANIMAL_DETECTION = 42
    BINARY_ON_OFF = 7
    CAMERA_DVR_CAPABLE = 72
    CANNOT_REPORT_STATUS = 33
    CAN_CHIME = 4
    CAN_INITIATE_CALL = 66
    CAN_LOCK_UNLOCK = 30
    CHIME_EXTENDER = 36
    CLIP_CAPTURE = 3
    DELETE_ALL_EVENTS = 63
    DETER = 45
    DETER_LIGHT = 52
    DETER_LINGER_DURATION = 53
    DETER_SCHEDULE = 50
    DETER_TONE = 51
    DETER_ZONE = 49
    DIMMABLE = 8
    DOORBELL_CHIME_SELECTABLE = 56
    DOOR_STATE = 71
    FAN15_MINUTE = 18
    FAN30_MINUTE = 19
    FAN45_MINUTE = 20
    FAN60_MINUTE = 21
    FAN120_MINUTE = 23
    FAN240_MINUTE = 24
    FAN480_MINUTE = 25
    FAN960_MINUTE = 26
    HAS_MICROPHONE = 46
    HSB_LIGHTING = 9
    HUMIDITY = 64
    HUMIDITY_CONTROL = 65
    IN_HOME_CHIME_VOLUME = 54
    LIVE_VIDEO = 6
    LURKER_DETECTION = 38
    MAINTAIN_ZOOM = 48
    MAXIMUM_TEMPERATURE = 12
    MAX_COOL_LOCK_SET_POINT = 69
    MAX_HEAT_LOCK_SET_POINT = 67
    MINIMUM_TEMPERATURE = 11
    MIN_COOL_LOCK_SET_POINT = 70
    MIN_HEAT_LOCK_SET_POINT = 68
    MIN_SETPOINT_DIFFERENCE_C = 13
    MIN_SETPOINT_DIFFERENCE_F = 14
    MOBILE_BLACKLISTABLE = 31
    MOTION_DETECTION = 1
    MUTE_CHIME = 55
    NIGHT_VISION = 60
    PACKAGE_DETECTION = 39
    PACKAGE_MOVE_DETECTION = 40
    PERSON_DETECTION = 16
    PINCH_TO_ZOOM = 32
    POLYGON_ROI = 44
    PREVIEW_CHIME_IN_HOME = 58
    PRIVACY_MODE = 15
    QUIET_MODE = 17
    REBOOT_CAMERA = 62
    RECT_ROI = 47
    RESTORE_DEFAULTS = 61
    ROTATE_IMAGE = 34
    SECURITY_2_0 = 27
    SET_POINT_LOCK = 66
    SIREN_EXTENDER = 37
    SOFT_DIP_SWITCH = 29
    STATUS_LIGHT_TOGGLE = 35
    TEMPERATURE_DETECTION = 10
    TWO_WAY_AUDIO = 5
    VEHICLE_DETECTION = 41
    VIDEO_QUALITY = 59
    VISITOR_CHIME_SELECTABLE = 57
    VISITOR_DETECTION = 2
    WARPED = 43
    WI_FI = 28
    ZWAVE_DIAGNOSTICS = 22

    # Handle unknown/future capabilities
    UNKNOWN = 0

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class DeviceType(Enum):
    """Vivint supported device types."""

    BINARY_SWITCH = "binary_switch_device"
    CAMERA = "camera_device"
    DOOR_LOCK = "door_lock_device"
    GARAGE_DOOR = "garage_door_device"
    MULTILEVEL_SWITCH = "multilevel_switch_device"
    THERMOSTAT = "thermostat_device"
    TOUCH_PANEL = "primary_touch_link_device"
    WIRELESS_SENSOR = "wireless_sensor"
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class EquipmentCode(IntEnum):
    """Equipment code."""

    APOLLO_COMBO_CO = 1422
    APOLLO_COMBO_SMOKE = 1322
    CARBON_MONOXIDE_DETECTOR_345_MHZ = 1254
    CO1_CO = 860
    CO1_CO_CANADA = 859
    CO3_2_GIG_CO = 1026
    DBELL1_2_GIG_DOORBELL = 1063
    DW10_THIN_DOOR_WINDOW = 862
    DW11_THIN_DOOR_WINDOW = 1251
    DW20_RECESSED_DOOR = 863
    DW21_R_RECESSED_DOOR = 1252
    EXISTING_CO = 692
    EXISTING_DOOR_WINDOW_CONTACT = 655
    EXISTING_FLOOD_TEMP = 556
    EXISTING_GLASS_BREAK = 475
    EXISTING_HEAT = 708
    EXISTING_KEY_FOB_REMOTE = 577
    EXISTING_MOTION_DETECTOR = 609
    EXISTING_SMOKE = 616
    FIREFIGHTER_AUDIO_DETECTOR = 1269
    GARAGE01_RESOLUTION_TILT = 1061
    GB1_GLASS_BREAK = 864
    GB2_GLASS_BREAK = 1248
    HW_DW_5816 = 673
    HW_FLOOD_SENSOR_5821 = 624
    HW_GLASS_BREAK_5853 = 519
    HW_HEAT_SENSOR_5809 = 557
    HW_PANIC_PENDANT_5802_MN2 = 491
    HW_PIR_5890 = 533
    HW_PIR_5894_PI = 530
    HW_R_DW_5818_MNL = 470
    HW_SMOKE_5808_W3 = 589
    KEY1_345_4_BUTTON_KEY_FOB_REMOTE = 866
    OTHER = 0
    PAD1_345_WIRELESS_KEYPAD = 867
    PANIC1 = 868
    PANIC2 = 1253
    PIR1_MOTION = 869
    PIR2_MOTION = 1249
    RE219_FLOOD_SENSOR = 1128
    RE220_T_2_GIG_REPEATER = 1144
    RE224_DT_DSC_TRANSLATOR = 1208
    RE224_GT_GE_TRANSLATOR = 941
    RE508_X_REPEATER = 2832
    RE524_X_WIRELESS_TAKEOVER = 2830
    REPEATER_345_MHZ = 2081
    SECURE_KEY_345_MHZ = 1250
    SMKE1_SMOKE = 872
    SMKE1_SMOKE_CANADA = 871
    SMKT2_GE_SMOKE_HEAT = 895
    SMKT3_2_GIG = 1058
    SMKT6_2_GIG = 1066
    SWS1_SMART_WATER_SENSOR = 1264
    TAKE_TAKEOVER = 873
    TILT_SENSOR_2_GIG_345 = 2831
    VS_CO3_DETECTOR = 1266
    VS_SMKT_SMOKE_DETECTOR = 1267

    # Handle unknown/future equipment codes
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class EquipmentType(IntEnum):
    """Equipment type."""

    CONTACT = 1
    EMERGENCY = 11
    FREEZE = 6
    MOTION = 2
    TEMPERATURE = 10
    WATER = 8
    UNKNOWN = 0

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class FanMode(IntEnum):
    """Fan mode."""

    AUTO_LOW = 0
    ON_LOW = 1
    AUTO_HIGH = 2
    ON_HIGH = 3
    TIMER_15 = 99
    TIMER_30 = 100
    TIMER_45 = 102
    TIMER_60 = 101
    TIMER_120 = 103
    TIMER_240 = 104
    TIMER_480 = 105
    TIMER_720 = 107
    TIMER_960 = 106

    # Handle unknown/future fan modes
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class GarageDoorState(IntEnum):
    """Garage door state."""

    UNKNOWN = 0
    CLOSED = 1
    CLOSING = 2
    STOPPED = 3
    OPENING = 4
    OPENED = 5


@unique
class HoldMode(IntEnum):
    """Hold mode."""

    BY_SCHEDULE = 0
    UNTIL_NEXT = 1
    TWO_HOURS = 2
    PERMANENT = 3


@unique
class OperatingMode(IntEnum):
    """Operating mode."""

    OFF = 0
    HEAT = 1
    COOL = 2
    AUTO = 3
    EMERGENCY_HEAT = 4
    RESUME = 5
    FAN_ONLY = 6
    FURNACE = 7
    DRY_AIR = 8
    MOIST_AIR = 9
    AUTO_CHANGEOVER = 10
    ENERGY_SAVE_HEAT = 11
    ENERGY_SAVE_COOL = 12
    AWAY = 13
    ECO = 100


@unique
class OperatingState(IntEnum):
    """Operating state."""

    IDLE = 0
    HEATING = 1
    COOLING = 2


@unique
class SensorType(IntEnum):
    """Sensor type."""

    AUDIBLE_ALARM = 7
    AUXILIARY_ALARM = 8
    CARBON_MONOXIDE = 14
    DAY_ZONE = 5
    EXIT_ENTRY_1 = 1
    EXIT_ENTRY_2 = 2
    FIRE = 9
    FIRE_WITH_VERIFICATION = 16
    INTERIOR_FOLLOWER = 4
    INTERIOR_WITH_DELAY = 10
    NO_RESPONSE = 23
    PERIMETER = 3
    REPEATER = 25
    SILENT_ALARM = 6
    SILENT_BURGLARY = 24
    UNUSED = 0

    # Handle unknown/future sensor types.
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class ZoneBypass(IntEnum):
    """Zone bypass statuses."""

    UNBYPASSED = 0
    FORCE_BYPASSED = 1
    MANUALLY_BYPASSED = 2

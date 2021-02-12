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
class DeviceType(Enum):
    """Vivint supported device types."""

    CAMERA = "camera_device"
    DOOR_LOCK = "door_lock_device"
    GARAGE_DOOR = "garage_door_device"
    LIGHT_MODULE = "multilevel_switch_device"
    THERMOSTAT = "thermostat_device"
    TOUCH_PANEL = "primary_touch_link_device"
    WIRELESS_SENSOR = "wireless_sensor"
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@unique
class EquipmentCode(IntEnum):
    """Vivint equipment code."""

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

    @classmethod
    def _missing_(cls, value):
        return cls.OTHER


@unique
class EquipmentType(IntEnum):
    """Vivint equipment type."""

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
class GarageDoorState(IntEnum):
    """Garage door state."""

    UNKNOWN = 0
    CLOSED = 1
    CLOSING = 2
    STOPPED = 3
    OPENING = 4
    OPENED = 5


@unique
class SensorType(IntEnum):
    """Vivint sensor type."""

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

    @classmethod
    def _missing_(cls, value):
        return cls.UNUSED


@unique
class ZoneBypass(IntEnum):
    """Zone bypass statuses."""

    UNBYPASSED = 0
    FORCE_BYPASSED = 1
    MANUALLY_BYPASSED = 2

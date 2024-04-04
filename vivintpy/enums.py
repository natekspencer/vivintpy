"""Module that defines various enums."""

from __future__ import annotations

import logging
from enum import Enum, IntEnum, unique
from typing import Any

_LOGGER = logging.getLogger(__name__)


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

    # Handle unknown/future armed state
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> ArmedState:
        _LOGGER.debug("Unknown armed state value: %s", value)
        return cls.UNKNOWN


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
    KEYPAD = 10
    PLATFORM = 11

    # Handle unknown/future capability category type
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> CapabilityCategoryType:
        _LOGGER.debug("Unknown capability category type value: %s", value)
        return cls.UNKNOWN


class CapabilityType(IntEnum):
    """Capability type."""

    ANIMAL_DETECTION = 42
    BINARY_ON_OFF = 7
    CAMERA_DVR_CAPABLE = 72
    CAN_CHIME = 4
    CAN_ENABLE_DISABLE_AUDIO = 73
    CAN_ENABLE_DISABLE_LED = 74
    CAN_INITIATE_CALL = 66
    CAN_LOCK_UNLOCK = 30
    CANNOT_REPORT_STATUS = 33
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
    DOOR_STATE = 71
    DOORBELL_CHIME_SELECTABLE = 56
    FAN120_MINUTE = 23
    FAN15_MINUTE = 18
    FAN240_MINUTE = 24
    FAN30_MINUTE = 19
    FAN45_MINUTE = 20
    FAN480_MINUTE = 25
    FAN60_MINUTE = 21
    FAN960_MINUTE = 26
    HAS_MICROPHONE = 46
    HAS_USER_CODE = 75
    HSB_LIGHTING = 9
    HUMIDITY = 64
    HUMIDITY_CONTROL = 65
    IN_HOME_CHIME_VOLUME = 54
    LED_BEEPER_SETTINGS = 73
    LIVE_VIDEO = 6
    LURKER_DETECTION = 38
    MAINTAIN_ZOOM = 48
    MAX_COOL_LOCK_SET_POINT = 69
    MAX_HEAT_LOCK_SET_POINT = 67
    MAXIMUM_TEMPERATURE = 12
    MIN_COOL_LOCK_SET_POINT = 70
    MIN_HEAT_LOCK_SET_POINT = 68
    MIN_SETPOINT_DIFFERENCE_C = 13
    MIN_SETPOINT_DIFFERENCE_F = 14
    MINIMUM_TEMPERATURE = 11
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

    # Handle unknown/future capability type
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> CapabilityType:
        _LOGGER.debug("Unknown capability type value: %s", value)
        return cls.UNKNOWN


# @unique
class DeviceType(Enum):
    """Device type."""

    AIR_TOWER = "airtower_device"
    ALPHA_CS6022_CAMERA = "alpha_cs6022_camera_device"
    BINARY_SWITCH = "binary_switch_device"
    CAMERA = "camera_device"
    CARGUARD_DEVICE = "carguard_device"
    DISPLAY_DEVICE = "display_device"
    DOOR_LOCK = "door_lock_device"
    ENERGY_SERVICE = "energy_service"
    GARAGE_DOOR = "garage_door_device"
    GROUP_DEVICE = "group_device"
    HSB_SWITCH = "multilevel_switch_ip_device"
    HUE_BRIDGE = "phillips_hue_bridge_device"
    IOT_SERVICE = "iot_service"
    KEY_FOB = "keyfob_device"
    KEY_PAD = "keypad_device"
    KWIKSET988_DOOR_LOCK = "kwikset_988_door_lock_device"
    MQTT_AUDIO_SYNC_SERVICE = "mqtt_audio_sync_service"
    MULTI_LEVEL_SWITCH = "multilevel_switch_device"
    NEST_THERMOSTAT = "nest_thermostat_device"
    NETWORK_HOSTS_SERVICE = "network_hosts_service"
    PANEL = "primary_touch_link_device"
    PANEL_DIAGNOSTICS_SERVICE = "panel_diagnostics_service"
    PERSONAL_GUARD_DEVICE = "personal_guard_device"
    POD_MY_Q_GARAGE_DOOR_DEVICE = "pod_myq_garage_door_device"
    POD_NEST_THERMOSTAT = "pod_nest_thermostat_device"
    SCHEDULER_SERVICE = "scheduler_service"
    SECURITY_SERVICE = "security_service"
    SENSOR_GROUP = "sensor_group"
    SLIMLINE = "slim_line_device"
    SMART_THERMOSTAT = "ct200_thermostat_device"
    SMART_THERMOSTAT_V2 = "ev2_thermostat_device"
    SPACE_MONKEY = "space_monkey_service"
    THERMOSTAT = "thermostat_device"
    VIVINT_DBC300_CAMERA = "vivint_dbc300_camera_device"
    VIVINT_DBC301_CAMERA = "vivint_dbc301_camera_device"
    VIVINT_DBC350_CAMERA = "vivint_dbc350_camera_device"
    VIVINT_ODC300_CAMERA = "vivint_odc300_camera_device"
    VIVINT_ODC350_CAMERA = "vivint_odc350_camera_device"
    VIVOTEK620_PT_CAMERA = "vivotek_620pt_camera_device"
    VIVOTEK720_CAMERA = "vivotek_720_camera_device"
    VIVOTEK720_W_CAMERA = "vivotek_720w_camera_device"
    VIVOTEK_DB8331_W_CAMERA = "vivotek_db8331w_camera_device"
    VIVOTEK_DB8332_CAMERA = "vivotek_db8332_camera_device"
    VIVOTEK_DB8332_S1_CAMERA = "vivotek_db8332s1_camera_device"
    VIVOTEK_DB8332_SW_CAMERA = "vivotek_db8332sw_camera_device"
    VIVOTEK_HD400_W_CAMERA = "vivotek_hd400w_camera_device"
    VIVOTEK_HDP450_CAMERA = "vivotek_hdp450_camera_device"
    WIRED_SENSOR = "wired_sensor"
    WIRELESS_SENSOR = "wireless_sensor"
    YOFI_DEVICE = "yofi_device"
    ZWAVE_KEY_PAD = "keypad_entry_device"

    # Deprecated
    MULTILEVEL_SWITCH = MULTI_LEVEL_SWITCH
    TOUCH_PANEL = PANEL

    UNKNOWN = None

    @classmethod
    def _missing_(cls, value: Any) -> DeviceType:
        _LOGGER.debug("Unknown device type value: %s", value)
        return cls.UNKNOWN


@unique
class EquipmentCode(IntEnum):
    """Equipment code."""

    APOLLO_COMBO_CO = 4050
    APOLLO_COMBO_SMOKE = 4040
    CARBON_MONOXIDE_DETECTOR_345_MHZ = 1254
    CO1_CO = 860
    CO1_CO_CANADA = 859
    CO3_2_GIG_CO = 1026
    DBELL1_2_GIG_DOORBELL = 1063
    DW10_THIN_DOOR_WINDOW = 862
    DW11_THIN_DOOR_WINDOW = 1251
    DW12_THIN_DOOR_WINDOW = 4000
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
    GB3_GLASS_BREAK = 4030
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
    PANIC3 = 4130
    PIR1_MOTION = 869
    PIR2_MOTION = 1249
    PIR3_MOTION = 4020
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

    # Handle unknown/future equipment code
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> EquipmentCode:
        _LOGGER.debug("Unknown equipment code value: %s", value)
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

    # Handle unknown/future equipment type
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> EquipmentType:
        _LOGGER.debug("Unknown equipment type value: %s", value)
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

    # Handle unknown/future fan mode
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> FanMode:
        _LOGGER.debug("Unknown fan mode value: %s", value)
        return cls.UNKNOWN


class FeatureType(Enum):
    """Feature type."""

    ANY_DETER = "any_deter"
    ANY_HVAC_AWAY_SETBACK = "any_hvac_away_setback"
    ANY_HVAC_SCHEDULES = "any_hvac_schedules"
    ANY_LOCK_SELECTION = "any_lock_selection"
    ANY_NIGHT_VISION = "any_nght"
    ANY_REBOOT = "any_rb"
    ANY_RESTORE_DEFAULTS = "any_rstdef"
    ANY_SMART_SENTRY_SNOOZE = "any_smart_sentry_snooze"
    ANY_VEHICLE_DETECTION = "any_vehicle_detection"
    ANY_VIDEO_THUMBNAILS = "any_video_thumbnails"

    DETER = "deter"
    DYNAMIC_CHIMES = "dynamic_chimes_available"
    HVAC_AWAY_SETBACK = "hvac_away_setback"
    HVAC_SCHEDULES = "hvac_schedules"
    LOCK_SELECTION = "lock_selection"
    PACKAGE_WATCH = "package_watch"
    REBOOT = "rb"
    RESTORE_DEFAULTS = "rstdef"
    SELECTABLE_NIGHTVISION = "nght"
    SMART_SENTRY_SNOOZE = "smart_sentry_snooze"
    VEHICLE_DETECTION = "vehicle_detection"
    VIDEO_THUMBNAILS = "video_thumbnails"

    UKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> FeatureType:
        _LOGGER.debug("Unknown feature type value: %s", value)
        return cls.UKNOWN


@unique
class GarageDoorState(IntEnum):
    """Garage door state."""

    UNKNOWN = 0
    CLOSED = 1
    CLOSING = 2
    STOPPED = 3
    OPENING = 4
    OPENED = 5

    @classmethod
    def _missing_(cls, value: Any) -> GarageDoorState:
        _LOGGER.debug("Unknown garage door state value: %s", value)
        return cls.UNKNOWN


@unique
class HoldMode(IntEnum):
    """Hold mode."""

    BY_SCHEDULE = 0
    UNTIL_NEXT = 1
    TWO_HOURS = 2
    PERMANENT = 3

    # Handle unknown/future hold mode
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> HoldMode:
        _LOGGER.debug("Unknown hold mode value: %s", value)
        return cls.UNKNOWN


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

    # Handle unknown/future operating mode
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> OperatingMode:
        _LOGGER.debug("Unknown operating mode value: %s", value)
        return cls.UNKNOWN


@unique
class OperatingState(IntEnum):
    """Operating state."""

    IDLE = 0
    HEATING = 1
    COOLING = 2

    # Handle unknown/future operating state
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> OperatingState:
        _LOGGER.debug("Unknown operating state value: %s", value)
        return cls.UNKNOWN


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

    # Handle unknown/future sensor type.
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> SensorType:
        _LOGGER.debug("Unknown sensor type value: %s", value)
        return cls.UNKNOWN


@unique
class ZoneBypass(IntEnum):
    """Zone bypass statuses."""

    UNBYPASSED = 0
    FORCE_BYPASSED = 1
    MANUALLY_BYPASSED = 2

    # Handle unknown/future zone bypass.
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: Any) -> ZoneBypass:
        _LOGGER.debug("Unknown zone bypass value: %s", value)
        return cls.UNKNOWN

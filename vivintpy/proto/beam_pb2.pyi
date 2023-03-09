from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

AGGLEVELNONE: DeterAggressionLevel
ALERT: PackageChime
ALWAYS: DeterScheduleType
ANIMAL_DETER: DeterScheduleType
ARMED: DeterScheduleType
BELLS: DoorbellChime
BREATH: DeterLightPattern
CUSTOM_ACTION: DeterScheduleType
DC_NONE: DoorbellChime
DESCRIPTOR: _descriptor.FileDescriptor
DINGALING: VisitorChime
DOORBELL: ChimeType
DOORBELL_DYNAMIC: DoorbellChime
DROPS: VisitorChime
ELEVATOR: DoorbellChime
ELEVATOR2: DoorbellChime
FAIR: VideoQuality
FIVE: DeterAggressionLevel
FLASH: DeterLightPattern
FOUR: DeterAggressionLevel
FRIENDLY: PackageChime
GOOD: VideoQuality
GREAT: VideoQuality
HELLO: PackageChime
HI: VisitorChime
HIGH_DOUBLE: VisitorChime
INSIGHT: VisitorChime
INVALID_CHIME_TYPE: ChimeType
LEFT_SIDE: DoorbellPosition
LEFT_WALL: DoorbellPosition
LIGHT_ONLY: PackageChime
LOW: VideoQuality
LOW_DOUBLE: VisitorChime
LURKER_DETER: DeterScheduleType
MEDIUM: VideoQuality
MELODY: DoorbellChime
MELODY2: DoorbellChime
MODERN: DoorbellChime
NEVER: DeterScheduleType
ONE: DeterAggressionLevel
PACKAGE: ChimeType
PACKAGE_APPROACHED_DETER: DeterScheduleType
PACKAGE_DETER: DeterScheduleType
PACKAGE_DYNAMIC: PackageChime
PACKAGE_MOVED_DETER: DeterScheduleType
PC_10: PackageChime
PC_11: PackageChime
PC_12: PackageChime
PC_13: PackageChime
PC_14: PackageChime
PC_15: PackageChime
PC_8: PackageChime
PC_9: PackageChime
PC_NONE: PackageChime
PERSON_DETER: DeterScheduleType
PIANO: VisitorChime
RECORDING: PackageChime
RECORD_FOR_EVERYWHERE: RecordForRegions
RECORD_FOR_PROPERTY: RecordForRegions
RECORD_FOR_REGIONS_NOTSET: RecordForRegions
RED: DeterLightColor
RIGHT_SIDE: DoorbellPosition
RIGHT_WALL: DoorbellPosition
SCALE: PackageChime
SCHEDULED: DeterScheduleType
SCHTYPENONE: DeterScheduleType
SEVEN: DeterAggressionLevel
SIX: DeterAggressionLevel
SNOOZE: DeterScheduleType
SOLID: DeterLightPattern
SPOTLIGHT_MODE_CALIBRATE: SpotlightMode
SPOTLIGHT_MODE_DETER: SpotlightMode
SPOTLIGHT_MODE_FLOOD: SpotlightMode
SPOTLIGHT_MODE_OFF: SpotlightMode
SPOTLIGHT_MODE_STARTUP: SpotlightMode
SPOTLIGHT_MODE_TRACK: SpotlightMode
SPOTLIGHT_STATUS_BAD_DEVICE: SpotlightStatus
SPOTLIGHT_STATUS_INVALID_COMMAND: SpotlightStatus
SPOTLIGHT_STATUS_NO_HARDWARE: SpotlightStatus
SPOTLIGHT_STATUS_NO_HW_VERSION: SpotlightStatus
SPOTLIGHT_STATUS_NO_LED_POWER: SpotlightStatus
SPOTLIGHT_STATUS_NO_TEMPERATURE: SpotlightStatus
SPOTLIGHT_STATUS_SUCCESS: SpotlightStatus
SPOTLIGHT_STATUS_UNKNOWN_ERROR: SpotlightStatus
SUCCESS: VisitorChime
THREE: DeterAggressionLevel
TRADITIONAL: DoorbellChime
TRADITIONAL2: DoorbellChime
TWO: DeterAggressionLevel
UNKNOWN_OBJECT_DETER: DeterScheduleType
UNSET: DoorbellPosition
USER_OVERRIDE: DeterScheduleType
VC_NONE: VisitorChime
VEHICLE_DETER: DeterScheduleType
VEHICLE_LEAVING_DETER: DeterScheduleType
VISITOR: ChimeType
VISITOR_DYNAMIC: VisitorChime
VQ_ZERO: VideoQuality
WAVE: VisitorChime
WHISTLE: PackageChime
YELLOW: DeterLightColor

class AccessPointInfo(_message.Message):
    __slots__ = ["channel", "encryption_types", "mac_addr", "signal_percent", "ssid", "unknown"]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTION_TYPES_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDR_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_PERCENT_FIELD_NUMBER: _ClassVar[int]
    SSID_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    channel: int
    encryption_types: str
    mac_addr: str
    signal_percent: int
    ssid: str
    unknown: int
    def __init__(self, channel: _Optional[int] = ..., ssid: _Optional[str] = ..., mac_addr: _Optional[str] = ..., encryption_types: _Optional[str] = ..., signal_percent: _Optional[int] = ..., unknown: _Optional[int] = ...) -> None: ...

class AddCameraToHubRequest(_message.Message):
    __slots__ = ["camera_type", "ip_address", "panel_id", "urn", "uuid"]
    CAMERA_TYPE_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    URN_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    camera_type: str
    ip_address: str
    panel_id: int
    urn: str
    uuid: str
    def __init__(self, panel_id: _Optional[int] = ..., camera_type: _Optional[str] = ..., uuid: _Optional[str] = ..., ip_address: _Optional[str] = ..., urn: _Optional[str] = ...) -> None: ...

class AdjustCameraToXyzRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "stream_id", "x", "y", "z"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    stream_id: str
    x: int
    y: int
    z: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., stream_id: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., z: _Optional[int] = ...) -> None: ...

class AdjustCameraToXyzResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class AspectRatioTuple(_message.Message):
    __slots__ = ["height", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    def __init__(self, width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class AssociateDvrRequest(_message.Message):
    __slots__ = ["panel_id", "space_monkey_hardware_id"]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    SPACE_MONKEY_HARDWARE_ID_FIELD_NUMBER: _ClassVar[int]
    panel_id: int
    space_monkey_hardware_id: str
    def __init__(self, panel_id: _Optional[int] = ..., space_monkey_hardware_id: _Optional[str] = ...) -> None: ...

class AssociateDvrResponse(_message.Message):
    __slots__ = ["dvr_service_id"]
    DVR_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    dvr_service_id: str
    def __init__(self, dvr_service_id: _Optional[str] = ...) -> None: ...

class BeamPortalCommand(_message.Message):
    __slots__ = ["setEnabledSpotlightZonesBitfield", "uuid"]
    SETENABLEDSPOTLIGHTZONESBITFIELD_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    setEnabledSpotlightZonesBitfield: int
    uuid: str
    def __init__(self, uuid: _Optional[str] = ..., setEnabledSpotlightZonesBitfield: _Optional[int] = ...) -> None: ...

class CameraThumbnailRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "partition_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PARTITION_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    partition_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., partition_id: _Optional[int] = ...) -> None: ...

class CameraThumbnailResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class Capabilities(_message.Message):
    __slots__ = ["type_capability"]
    TYPE_CAPABILITY_FIELD_NUMBER: _ClassVar[int]
    type_capability: _containers.RepeatedCompositeFieldContainer[TypeCapabilities]
    def __init__(self, type_capability: _Optional[_Iterable[_Union[TypeCapabilities, _Mapping]]] = ...) -> None: ...

class Date(_message.Message):
    __slots__ = ["day", "month", "year"]
    DAY_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    day: int
    month: int
    year: int
    def __init__(self, year: _Optional[int] = ..., month: _Optional[int] = ..., day: _Optional[int] = ...) -> None: ...

class DeleteAllEventsRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class DeleteAllEventsResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class DeleteCameraRequest(_message.Message):
    __slots__ = ["device_id", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class DeleteCameraResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class DetectionWindow(_message.Message):
    __slots__ = ["height", "index", "object_size", "origin_x", "origin_y", "sensitivity", "width"]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SIZE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_X_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_Y_FIELD_NUMBER: _ClassVar[int]
    SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    height: float
    index: int
    object_size: float
    origin_x: float
    origin_y: float
    sensitivity: float
    width: float
    def __init__(self, origin_x: _Optional[float] = ..., origin_y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., sensitivity: _Optional[float] = ..., object_size: _Optional[float] = ..., index: _Optional[int] = ...) -> None: ...

class DeterSchedule(_message.Message):
    __slots__ = ["fri", "local_end_minutes", "local_start_minutes", "mon", "sat", "sun", "thu", "tue", "wed"]
    FRI_FIELD_NUMBER: _ClassVar[int]
    LOCAL_END_MINUTES_FIELD_NUMBER: _ClassVar[int]
    LOCAL_START_MINUTES_FIELD_NUMBER: _ClassVar[int]
    MON_FIELD_NUMBER: _ClassVar[int]
    SAT_FIELD_NUMBER: _ClassVar[int]
    SUN_FIELD_NUMBER: _ClassVar[int]
    THU_FIELD_NUMBER: _ClassVar[int]
    TUE_FIELD_NUMBER: _ClassVar[int]
    WED_FIELD_NUMBER: _ClassVar[int]
    fri: bool
    local_end_minutes: int
    local_start_minutes: int
    mon: bool
    sat: bool
    sun: bool
    thu: bool
    tue: bool
    wed: bool
    def __init__(self, sun: bool = ..., mon: bool = ..., tue: bool = ..., wed: bool = ..., thu: bool = ..., fri: bool = ..., sat: bool = ..., local_start_minutes: _Optional[int] = ..., local_end_minutes: _Optional[int] = ...) -> None: ...

class DeterScheduleSettingsV2(_message.Message):
    __slots__ = ["deter_schedule_types", "schedule"]
    DETER_SCHEDULE_TYPES_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    deter_schedule_types: _containers.RepeatedScalarFieldContainer[DeterScheduleType]
    schedule: DeterSchedule
    def __init__(self, deter_schedule_types: _Optional[_Iterable[_Union[DeterScheduleType, str]]] = ..., schedule: _Optional[_Union[DeterSchedule, _Mapping]] = ...) -> None: ...

class DynamicChimeBannerInfo(_message.Message):
    __slots__ = ["BackgroundAnimation", "MainAnimation", "headline", "subhead"]
    BACKGROUNDANIMATION_FIELD_NUMBER: _ClassVar[int]
    BackgroundAnimation: str
    HEADLINE_FIELD_NUMBER: _ClassVar[int]
    MAINANIMATION_FIELD_NUMBER: _ClassVar[int]
    MainAnimation: str
    SUBHEAD_FIELD_NUMBER: _ClassVar[int]
    headline: str
    subhead: str
    def __init__(self, headline: _Optional[str] = ..., subhead: _Optional[str] = ..., MainAnimation: _Optional[str] = ..., BackgroundAnimation: _Optional[str] = ...) -> None: ...

class DynamicChimeCategory(_message.Message):
    __slots__ = ["availability_end", "availability_start", "dynamic_chime_banner_info", "dynamic_chime_info", "dynamic_chime_splash_page_info", "id", "name", "ui_availability_copy"]
    AVAILABILITY_END_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_START_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_CHIME_BANNER_INFO_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_CHIME_INFO_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_CHIME_SPLASH_PAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UI_AVAILABILITY_COPY_FIELD_NUMBER: _ClassVar[int]
    availability_end: _timestamp_pb2.Timestamp
    availability_start: _timestamp_pb2.Timestamp
    dynamic_chime_banner_info: DynamicChimeBannerInfo
    dynamic_chime_info: _containers.RepeatedCompositeFieldContainer[DynamicChimeInfo]
    dynamic_chime_splash_page_info: DynamicChimeSplashPageInfo
    id: str
    name: str
    ui_availability_copy: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., availability_start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., availability_end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ui_availability_copy: _Optional[str] = ..., dynamic_chime_info: _Optional[_Iterable[_Union[DynamicChimeInfo, _Mapping]]] = ..., dynamic_chime_banner_info: _Optional[_Union[DynamicChimeBannerInfo, _Mapping]] = ..., dynamic_chime_splash_page_info: _Optional[_Union[DynamicChimeSplashPageInfo, _Mapping]] = ...) -> None: ...

class DynamicChimeInfo(_message.Message):
    __slots__ = ["id", "name", "sha256hash", "url"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHA256HASH_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    sha256hash: str
    url: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ..., sha256hash: _Optional[str] = ...) -> None: ...

class DynamicChimeSplashPageBulletInfo(_message.Message):
    __slots__ = ["body", "headline"]
    BODY_FIELD_NUMBER: _ClassVar[int]
    HEADLINE_FIELD_NUMBER: _ClassVar[int]
    body: str
    headline: str
    def __init__(self, headline: _Optional[str] = ..., body: _Optional[str] = ...) -> None: ...

class DynamicChimeSplashPageInfo(_message.Message):
    __slots__ = ["Bullets", "Image_Android", "Image_iOS", "PrimaryButtonCopy", "headline"]
    BULLETS_FIELD_NUMBER: _ClassVar[int]
    Bullets: _containers.RepeatedCompositeFieldContainer[DynamicChimeSplashPageBulletInfo]
    HEADLINE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ANDROID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_IOS_FIELD_NUMBER: _ClassVar[int]
    Image_Android: str
    Image_iOS: str
    PRIMARYBUTTONCOPY_FIELD_NUMBER: _ClassVar[int]
    PrimaryButtonCopy: str
    headline: str
    def __init__(self, Image_iOS: _Optional[str] = ..., Image_Android: _Optional[str] = ..., headline: _Optional[str] = ..., Bullets: _Optional[_Iterable[_Union[DynamicChimeSplashPageBulletInfo, _Mapping]]] = ..., PrimaryButtonCopy: _Optional[str] = ...) -> None: ...

class GetAnalyticsOptInRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class GetAnalyticsOptInResponse(_message.Message):
    __slots__ = ["opt_in", "response"]
    OPT_IN_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    opt_in: bool
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., opt_in: bool = ...) -> None: ...

class GetCameraSettingsRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class GetCameraSettingsResponse(_message.Message):
    __slots__ = ["DeterScheduleV2", "aggression_level", "analytics_opt_in", "analytics_sensitivity", "animal_boundary_points", "aspect_ratio_tuple", "camera_connection_type", "capabilities", "chime_volume", "command_control_availability_state", "connected_to", "detection_windows", "deter_boundary_points", "deter_light_color", "deter_light_pattern", "deter_on_duty", "deter_override", "deter_override_end_timestamp", "deter_reason", "deter_schedule", "deter_schedule_version", "deter_timestamp", "deter_type", "deter_user_info", "deter_valid_schedule_types", "doorbell_chime", "doorbell_position", "dynamic_doorbell_chime_category_id", "dynamic_doorbell_chime_id", "dynamic_doorbell_chime_sha256hash", "dynamic_doorbell_chime_url", "enabled_spotlight_zones_bitfield", "extend_chime", "extend_siren", "features", "flip", "info", "ir_led_on", "led_on", "linger_duration", "lurker_deter", "mute_chime", "name", "network_availability_state", "night_vision", "notification_availability_state", "notify_on_animal_seen", "notify_on_deter", "notify_on_doorbell_press", "notify_on_lurker_detected", "notify_on_package_moved", "notify_on_package_seen", "notify_on_person_detected", "notify_on_vehicle_leaving", "notify_on_vehicle_seen", "package_boundary_points", "package_chime", "package_delivery_locations", "package_watch", "package_watch_state", "playback_enabled", "privacy_mode", "property_boundary_points", "quiet_mode", "record_audio", "record_for_regions", "record_on_deter", "record_on_doorbell_press", "record_on_lurker_detected", "record_on_package_detected", "record_on_person_detected", "record_on_vehicle_seen", "response", "smart_sentry_snooze_until", "smart_sentry_snooze_user_info", "spotlight_brightness", "spotlight_calibration", "spotlight_deter_lighting_behavior", "spotlight_driver_version", "spotlight_flood_state", "spotlight_follow", "spotlight_hardware_version", "spotlight_installed", "spotlight_light_on_person_detected", "spotlight_mode", "spotlight_night_light", "spotlight_night_mode", "spotlight_num_zones", "spotlight_status", "spotlight_temperature", "stream_availability_state", "vehicle_boundary_points", "video_clip_analytics_allowed", "video_quality", "visitor_chime", "zoom_lock"]
    AGGRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    ANALYTICS_OPT_IN_FIELD_NUMBER: _ClassVar[int]
    ANALYTICS_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    ANIMAL_BOUNDARY_POINTS_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIO_TUPLE_FIELD_NUMBER: _ClassVar[int]
    CAMERA_CONNECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    CHIME_VOLUME_FIELD_NUMBER: _ClassVar[int]
    COMMAND_CONTROL_AVAILABILITY_STATE_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_TO_FIELD_NUMBER: _ClassVar[int]
    DETECTION_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    DETERSCHEDULEV2_FIELD_NUMBER: _ClassVar[int]
    DETER_BOUNDARY_POINTS_FIELD_NUMBER: _ClassVar[int]
    DETER_LIGHT_COLOR_FIELD_NUMBER: _ClassVar[int]
    DETER_LIGHT_PATTERN_FIELD_NUMBER: _ClassVar[int]
    DETER_ON_DUTY_FIELD_NUMBER: _ClassVar[int]
    DETER_OVERRIDE_END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DETER_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    DETER_REASON_FIELD_NUMBER: _ClassVar[int]
    DETER_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    DETER_SCHEDULE_VERSION_FIELD_NUMBER: _ClassVar[int]
    DETER_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DETER_TYPE_FIELD_NUMBER: _ClassVar[int]
    DETER_USER_INFO_FIELD_NUMBER: _ClassVar[int]
    DETER_VALID_SCHEDULE_TYPES_FIELD_NUMBER: _ClassVar[int]
    DOORBELL_CHIME_FIELD_NUMBER: _ClassVar[int]
    DOORBELL_POSITION_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_DOORBELL_CHIME_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_DOORBELL_CHIME_ID_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_DOORBELL_CHIME_SHA256HASH_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_DOORBELL_CHIME_URL_FIELD_NUMBER: _ClassVar[int]
    DeterScheduleV2: DeterScheduleSettingsV2
    ENABLED_SPOTLIGHT_ZONES_BITFIELD_FIELD_NUMBER: _ClassVar[int]
    EXTEND_CHIME_FIELD_NUMBER: _ClassVar[int]
    EXTEND_SIREN_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    FLIP_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    IR_LED_ON_FIELD_NUMBER: _ClassVar[int]
    LED_ON_FIELD_NUMBER: _ClassVar[int]
    LINGER_DURATION_FIELD_NUMBER: _ClassVar[int]
    LURKER_DETER_FIELD_NUMBER: _ClassVar[int]
    MUTE_CHIME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NETWORK_AVAILABILITY_STATE_FIELD_NUMBER: _ClassVar[int]
    NIGHT_VISION_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_AVAILABILITY_STATE_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_ANIMAL_SEEN_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_DETER_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_DOORBELL_PRESS_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_LURKER_DETECTED_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_PACKAGE_MOVED_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_PACKAGE_SEEN_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_PERSON_DETECTED_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_VEHICLE_LEAVING_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_ON_VEHICLE_SEEN_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_BOUNDARY_POINTS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_CHIME_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_DELIVERY_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_WATCH_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_WATCH_STATE_FIELD_NUMBER: _ClassVar[int]
    PLAYBACK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    PRIVACY_MODE_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_BOUNDARY_POINTS_FIELD_NUMBER: _ClassVar[int]
    QUIET_MODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_AUDIO_FIELD_NUMBER: _ClassVar[int]
    RECORD_FOR_REGIONS_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_DETER_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_DOORBELL_PRESS_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_LURKER_DETECTED_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_PACKAGE_DETECTED_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_PERSON_DETECTED_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_VEHICLE_SEEN_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SMART_SENTRY_SNOOZE_UNTIL_FIELD_NUMBER: _ClassVar[int]
    SMART_SENTRY_SNOOZE_USER_INFO_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_CALIBRATION_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DETER_LIGHTING_BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DRIVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_FLOOD_STATE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_FOLLOW_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_HARDWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_LIGHT_ON_PERSON_DETECTED_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_MODE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_NIGHT_LIGHT_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_NIGHT_MODE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_NUM_ZONES_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_STATUS_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    STREAM_AVAILABILITY_STATE_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_BOUNDARY_POINTS_FIELD_NUMBER: _ClassVar[int]
    VIDEO_CLIP_ANALYTICS_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    VIDEO_QUALITY_FIELD_NUMBER: _ClassVar[int]
    VISITOR_CHIME_FIELD_NUMBER: _ClassVar[int]
    ZOOM_LOCK_FIELD_NUMBER: _ClassVar[int]
    aggression_level: DeterAggressionLevel
    analytics_opt_in: bool
    analytics_sensitivity: int
    animal_boundary_points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    aspect_ratio_tuple: AspectRatioTuple
    camera_connection_type: str
    capabilities: Capabilities
    chime_volume: int
    command_control_availability_state: int
    connected_to: str
    detection_windows: _containers.RepeatedCompositeFieldContainer[DetectionWindow]
    deter_boundary_points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    deter_light_color: DeterLightColor
    deter_light_pattern: DeterLightPattern
    deter_on_duty: bool
    deter_override: bool
    deter_override_end_timestamp: int
    deter_reason: DeterScheduleType
    deter_schedule: DeterSchedule
    deter_schedule_version: int
    deter_timestamp: int
    deter_type: DeterScheduleType
    deter_user_info: str
    deter_valid_schedule_types: _containers.RepeatedScalarFieldContainer[DeterScheduleType]
    doorbell_chime: DoorbellChime
    doorbell_position: DoorbellPosition
    dynamic_doorbell_chime_category_id: str
    dynamic_doorbell_chime_id: str
    dynamic_doorbell_chime_sha256hash: str
    dynamic_doorbell_chime_url: str
    enabled_spotlight_zones_bitfield: int
    extend_chime: bool
    extend_siren: bool
    features: _containers.RepeatedScalarFieldContainer[str]
    flip: bool
    info: TechnicalInfo
    ir_led_on: bool
    led_on: bool
    linger_duration: int
    lurker_deter: bool
    mute_chime: bool
    name: str
    network_availability_state: int
    night_vision: bool
    notification_availability_state: int
    notify_on_animal_seen: bool
    notify_on_deter: bool
    notify_on_doorbell_press: bool
    notify_on_lurker_detected: bool
    notify_on_package_moved: bool
    notify_on_package_seen: bool
    notify_on_person_detected: bool
    notify_on_vehicle_leaving: bool
    notify_on_vehicle_seen: bool
    package_boundary_points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    package_chime: PackageChime
    package_delivery_locations: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPoint]
    package_watch: bool
    package_watch_state: bool
    playback_enabled: bool
    privacy_mode: bool
    property_boundary_points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    quiet_mode: bool
    record_audio: bool
    record_for_regions: RecordForRegions
    record_on_deter: bool
    record_on_doorbell_press: bool
    record_on_lurker_detected: bool
    record_on_package_detected: bool
    record_on_person_detected: bool
    record_on_vehicle_seen: bool
    response: Response
    smart_sentry_snooze_until: int
    smart_sentry_snooze_user_info: str
    spotlight_brightness: float
    spotlight_calibration: SpotlightCalibrationData
    spotlight_deter_lighting_behavior: LightingBehavior
    spotlight_driver_version: str
    spotlight_flood_state: bool
    spotlight_follow: bool
    spotlight_hardware_version: str
    spotlight_installed: bool
    spotlight_light_on_person_detected: bool
    spotlight_mode: SpotlightMode
    spotlight_night_light: bool
    spotlight_night_mode: bool
    spotlight_num_zones: int
    spotlight_status: SpotlightStatus
    spotlight_temperature: float
    stream_availability_state: int
    vehicle_boundary_points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    video_clip_analytics_allowed: bool
    video_quality: VideoQuality
    visitor_chime: VisitorChime
    zoom_lock: bool
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., privacy_mode: bool = ..., playback_enabled: bool = ..., detection_windows: _Optional[_Iterable[_Union[DetectionWindow, _Mapping]]] = ..., chime_volume: _Optional[int] = ..., mute_chime: bool = ..., video_quality: _Optional[_Union[VideoQuality, str]] = ..., night_vision: bool = ..., flip: bool = ..., zoom_lock: bool = ..., led_on: bool = ..., record_audio: bool = ..., doorbell_chime: _Optional[_Union[DoorbellChime, str]] = ..., visitor_chime: _Optional[_Union[VisitorChime, str]] = ..., extend_chime: bool = ..., quiet_mode: bool = ..., name: _Optional[str] = ..., info: _Optional[_Union[TechnicalInfo, _Mapping]] = ..., ir_led_on: bool = ..., capabilities: _Optional[_Union[Capabilities, _Mapping]] = ..., aggression_level: _Optional[_Union[DeterAggressionLevel, str]] = ..., deter_type: _Optional[_Union[DeterScheduleType, str]] = ..., deter_schedule: _Optional[_Union[DeterSchedule, _Mapping]] = ..., property_boundary_points: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., deter_boundary_points: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., deter_light_color: _Optional[_Union[DeterLightColor, str]] = ..., deter_light_pattern: _Optional[_Union[DeterLightPattern, str]] = ..., linger_duration: _Optional[int] = ..., extend_siren: bool = ..., lurker_deter: bool = ..., record_for_regions: _Optional[_Union[RecordForRegions, str]] = ..., record_on_lurker_detected: bool = ..., record_on_package_detected: bool = ..., record_on_person_detected: bool = ..., analytics_sensitivity: _Optional[int] = ..., package_chime: _Optional[_Union[PackageChime, str]] = ..., connected_to: _Optional[str] = ..., camera_connection_type: _Optional[str] = ..., video_clip_analytics_allowed: bool = ..., package_watch: bool = ..., notify_on_person_detected: bool = ..., notify_on_lurker_detected: bool = ..., doorbell_position: _Optional[_Union[DoorbellPosition, str]] = ..., notify_on_package_seen: bool = ..., notify_on_package_moved: bool = ..., notify_on_vehicle_seen: bool = ..., notify_on_animal_seen: bool = ..., package_delivery_locations: _Optional[_Iterable[_Union[PropertyBoundaryPoint, _Mapping]]] = ..., smart_sentry_snooze_until: _Optional[int] = ..., package_watch_state: bool = ..., deter_schedule_version: _Optional[int] = ..., deter_on_duty: bool = ..., deter_reason: _Optional[_Union[DeterScheduleType, str]] = ..., deter_timestamp: _Optional[int] = ..., deter_user_info: _Optional[str] = ..., deter_override: bool = ..., deter_override_end_timestamp: _Optional[int] = ..., deter_valid_schedule_types: _Optional[_Iterable[_Union[DeterScheduleType, str]]] = ..., smart_sentry_snooze_user_info: _Optional[str] = ..., record_on_deter: bool = ..., notify_on_deter: bool = ..., features: _Optional[_Iterable[str]] = ..., DeterScheduleV2: _Optional[_Union[DeterScheduleSettingsV2, _Mapping]] = ..., analytics_opt_in: bool = ..., dynamic_doorbell_chime_category_id: _Optional[str] = ..., dynamic_doorbell_chime_id: _Optional[str] = ..., dynamic_doorbell_chime_url: _Optional[str] = ..., dynamic_doorbell_chime_sha256hash: _Optional[str] = ..., record_on_vehicle_seen: bool = ..., notify_on_doorbell_press: bool = ..., record_on_doorbell_press: bool = ..., aspect_ratio_tuple: _Optional[_Union[AspectRatioTuple, _Mapping]] = ..., animal_boundary_points: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., vehicle_boundary_points: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., package_boundary_points: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., command_control_availability_state: _Optional[int] = ..., notification_availability_state: _Optional[int] = ..., network_availability_state: _Optional[int] = ..., stream_availability_state: _Optional[int] = ..., notify_on_vehicle_leaving: bool = ..., spotlight_installed: bool = ..., spotlight_mode: _Optional[_Union[SpotlightMode, str]] = ..., spotlight_brightness: _Optional[float] = ..., spotlight_num_zones: _Optional[int] = ..., enabled_spotlight_zones_bitfield: _Optional[int] = ..., spotlight_follow: bool = ..., spotlight_deter_lighting_behavior: _Optional[_Union[LightingBehavior, _Mapping]] = ..., spotlight_status: _Optional[_Union[SpotlightStatus, str]] = ..., spotlight_temperature: _Optional[float] = ..., spotlight_driver_version: _Optional[str] = ..., spotlight_hardware_version: _Optional[str] = ..., spotlight_light_on_person_detected: bool = ..., spotlight_calibration: _Optional[_Union[SpotlightCalibrationData, _Mapping]] = ..., spotlight_night_mode: bool = ..., spotlight_night_light: bool = ..., spotlight_flood_state: bool = ...) -> None: ...

class GetCameraTechnicalInfoRequest(_message.Message):
    __slots__ = ["device_id", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class GetCameraTechnicalInfoResponse(_message.Message):
    __slots__ = ["info", "response"]
    INFO_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    info: TechnicalInfo
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., info: _Optional[_Union[TechnicalInfo, _Mapping]] = ...) -> None: ...

class GetClipSharingLinkRequest(_message.Message):
    __slots__ = ["header", "history_date", "history_record_id"]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    HISTORY_DATE_FIELD_NUMBER: _ClassVar[int]
    HISTORY_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    header: SettingsRequestHeader
    history_date: Date
    history_record_id: str
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., history_date: _Optional[_Union[Date, _Mapping]] = ..., history_record_id: _Optional[str] = ...) -> None: ...

class GetClipSharingLinkResponse(_message.Message):
    __slots__ = ["clip_sharing_link", "response"]
    CLIP_SHARING_LINK_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    clip_sharing_link: str
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., clip_sharing_link: _Optional[str] = ...) -> None: ...

class GetDeviceOnboardingRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class GetDeviceOnboardingResponse(_message.Message):
    __slots__ = ["analytics_opt_in", "camera_name", "camera_rotate", "deter_aggression_level", "deter_intro", "deter_schedule", "doorbell_position", "notifications", "package_delivery_locations", "package_watch", "property_boundary", "property_boundary_v2", "response", "spotlight_analytics_opt_in", "spotlight_camera_name", "spotlight_default_settings", "spotlight_deter_intro", "spotlight_deter_schedule", "spotlight_onboarding_done", "spotlight_splash"]
    ANALYTICS_OPT_IN_FIELD_NUMBER: _ClassVar[int]
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ROTATE_FIELD_NUMBER: _ClassVar[int]
    DETER_AGGRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    DETER_INTRO_FIELD_NUMBER: _ClassVar[int]
    DETER_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    DOORBELL_POSITION_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_DELIVERY_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_WATCH_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_BOUNDARY_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_BOUNDARY_V2_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_ANALYTICS_OPT_IN_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DEFAULT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DETER_INTRO_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DETER_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_ONBOARDING_DONE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_SPLASH_FIELD_NUMBER: _ClassVar[int]
    analytics_opt_in: bool
    camera_name: bool
    camera_rotate: bool
    deter_aggression_level: bool
    deter_intro: bool
    deter_schedule: bool
    doorbell_position: bool
    notifications: bool
    package_delivery_locations: bool
    package_watch: bool
    property_boundary: bool
    property_boundary_v2: bool
    response: Response
    spotlight_analytics_opt_in: bool
    spotlight_camera_name: bool
    spotlight_default_settings: bool
    spotlight_deter_intro: bool
    spotlight_deter_schedule: bool
    spotlight_onboarding_done: bool
    spotlight_splash: bool
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., property_boundary: bool = ..., notifications: bool = ..., deter_intro: bool = ..., deter_schedule: bool = ..., deter_aggression_level: bool = ..., camera_name: bool = ..., camera_rotate: bool = ..., analytics_opt_in: bool = ..., doorbell_position: bool = ..., package_delivery_locations: bool = ..., package_watch: bool = ..., property_boundary_v2: bool = ..., spotlight_splash: bool = ..., spotlight_deter_intro: bool = ..., spotlight_default_settings: bool = ..., spotlight_deter_schedule: bool = ..., spotlight_camera_name: bool = ..., spotlight_analytics_opt_in: bool = ..., spotlight_onboarding_done: bool = ...) -> None: ...

class GetDynamicChimesRequest(_message.Message):
    __slots__ = ["chime_category_id", "chime_id", "ignore_active_check", "panel_id"]
    CHIME_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    CHIME_ID_FIELD_NUMBER: _ClassVar[int]
    IGNORE_ACTIVE_CHECK_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    chime_category_id: str
    chime_id: str
    ignore_active_check: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., chime_id: _Optional[str] = ..., chime_category_id: _Optional[str] = ..., ignore_active_check: bool = ...) -> None: ...

class GetDynamicChimesResponse(_message.Message):
    __slots__ = ["dynamic_chimes", "response"]
    DYNAMIC_CHIMES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    dynamic_chimes: _containers.RepeatedCompositeFieldContainer[DynamicChimeCategory]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., dynamic_chimes: _Optional[_Iterable[_Union[DynamicChimeCategory, _Mapping]]] = ...) -> None: ...

class GetHistoryClipURLRequest(_message.Message):
    __slots__ = ["download", "header", "history_date", "history_record_id"]
    DOWNLOAD_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    HISTORY_DATE_FIELD_NUMBER: _ClassVar[int]
    HISTORY_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    download: bool
    header: SystemRequestHeader
    history_date: Date
    history_record_id: str
    def __init__(self, header: _Optional[_Union[SystemRequestHeader, _Mapping]] = ..., history_record_id: _Optional[str] = ..., history_date: _Optional[_Union[Date, _Mapping]] = ..., download: bool = ...) -> None: ...

class GetHistoryClipURLResponse(_message.Message):
    __slots__ = ["clip_url", "response"]
    CLIP_URL_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    clip_url: str
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., clip_url: _Optional[str] = ...) -> None: ...

class GetLegacyHistoryClipURLRequest(_message.Message):
    __slots__ = ["history_record_id"]
    HISTORY_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    history_record_id: str
    def __init__(self, history_record_id: _Optional[str] = ...) -> None: ...

class GetPanelLoginRequest(_message.Message):
    __slots__ = ["panel_id"]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ...) -> None: ...

class GetPanelLoginResponse(_message.Message):
    __slots__ = ["password", "response", "user"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    password: str
    response: Response
    user: str
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., user: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class GetPanelSettingsRequest(_message.Message):
    __slots__ = ["device_id", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class GetPanelSettingsResponse(_message.Message):
    __slots__ = ["doorbell_muted", "response"]
    DOORBELL_MUTED_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    doorbell_muted: bool
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., doorbell_muted: bool = ...) -> None: ...

class LightingBehavior(_message.Message):
    __slots__ = ["behavior"]
    class Behavior(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    BEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    CIRCLE: LightingBehavior.Behavior
    FLOOD: LightingBehavior.Behavior
    OFF: LightingBehavior.Behavior
    STROBE: LightingBehavior.Behavior
    TRACK: LightingBehavior.Behavior
    WAVE: LightingBehavior.Behavior
    behavior: LightingBehavior.Behavior
    def __init__(self, behavior: _Optional[_Union[LightingBehavior.Behavior, str]] = ...) -> None: ...

class PanelDeviceIds(_message.Message):
    __slots__ = ["device_id", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class PanelKillWiFiNetworkRequest(_message.Message):
    __slots__ = ["panel_id"]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ...) -> None: ...

class PanelRefreshSSIDListRequest(_message.Message):
    __slots__ = ["forWiFiConnect", "panel_id"]
    FORWIFICONNECT_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    forWiFiConnect: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., forWiFiConnect: bool = ...) -> None: ...

class PreviewChimeRequest(_message.Message):
    __slots__ = ["chime_type", "device_id", "panel_id"]
    CHIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    chime_type: ChimeType
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., chime_type: _Optional[_Union[ChimeType, str]] = ...) -> None: ...

class PreviewChimeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class PropertyBoundaryPoint(_message.Message):
    __slots__ = ["x", "y"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class PropertyBoundaryPointList(_message.Message):
    __slots__ = ["points"]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPoint]
    def __init__(self, points: _Optional[_Iterable[_Union[PropertyBoundaryPoint, _Mapping]]] = ...) -> None: ...

class RebootCameraRequest(_message.Message):
    __slots__ = ["device_id", "device_type", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    device_type: str
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., device_type: _Optional[str] = ...) -> None: ...

class RebootCameraResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class ReportVideoFailedRequest(_message.Message):
    __slots__ = ["app", "app_version", "camera_name", "count", "date", "device_id", "device_type", "interface", "mobile_device_id", "panel_id", "previous_stream_array", "reason", "session", "stream_name", "url"]
    APP_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    MOBILE_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STREAM_ARRAY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    app: str
    app_version: str
    camera_name: str
    count: int
    date: str
    device_id: int
    device_type: str
    interface: str
    mobile_device_id: str
    panel_id: int
    previous_stream_array: str
    reason: str
    session: str
    stream_name: str
    url: str
    def __init__(self, camera_name: _Optional[str] = ..., count: _Optional[int] = ..., date: _Optional[str] = ..., device_id: _Optional[int] = ..., device_type: _Optional[str] = ..., interface: _Optional[str] = ..., mobile_device_id: _Optional[str] = ..., panel_id: _Optional[int] = ..., previous_stream_array: _Optional[str] = ..., reason: _Optional[str] = ..., session: _Optional[str] = ..., url: _Optional[str] = ..., app: _Optional[str] = ..., stream_name: _Optional[str] = ..., app_version: _Optional[str] = ...) -> None: ...

class ReportVideoFailedResponse(_message.Message):
    __slots__ = ["request_id", "response"]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["timestamp"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class RestoreDefaultsRequest(_message.Message):
    __slots__ = ["device_id", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class RestoreDefaultsResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetAnalyticsOptInRequest(_message.Message):
    __slots__ = ["device_id", "header", "opt_in", "panel_id", "version"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    OPT_IN_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    opt_in: bool
    panel_id: int
    version: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., opt_in: bool = ..., version: _Optional[int] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetAnalyticsOptInResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetAnalyticsSensitivityRequest(_message.Message):
    __slots__ = ["analytics_sensitivity", "device_id", "panel_id"]
    ANALYTICS_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    analytics_sensitivity: int
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., analytics_sensitivity: _Optional[int] = ...) -> None: ...

class SetAnalyticsSensitivityResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetAnimalBoundaryRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id", "point_list"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_LIST_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    point_list: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., point_list: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetAnimalBoundaryResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetAudioRecordingRequest(_message.Message):
    __slots__ = ["audio_recording", "device_id", "header", "panel_id"]
    AUDIO_RECORDING_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    audio_recording: bool
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., audio_recording: bool = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetAudioRecordingResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetCameraListOrderRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "user_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: _containers.RepeatedScalarFieldContainer[int]
    panel_id: int
    user_id: str
    def __init__(self, panel_id: _Optional[int] = ..., user_id: _Optional[str] = ..., device_id: _Optional[_Iterable[int]] = ...) -> None: ...

class SetCameraListOrderResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetCameraPlaybackEnabledRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "playback_enabled"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYBACK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    playback_enabled: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., playback_enabled: bool = ...) -> None: ...

class SetCameraPlaybackEnabledResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetCameraPrivacyModeRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "privacy_mode"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PRIVACY_MODE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    privacy_mode: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., privacy_mode: bool = ...) -> None: ...

class SetCameraPrivacyModeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetCaptureClipOnRequest(_message.Message):
    __slots__ = ["enabled", "header"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., enabled: bool = ...) -> None: ...

class SetCaptureClipOnResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetChimeMuteRequest(_message.Message):
    __slots__ = ["device_id", "mute", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MUTE_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    mute: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., mute: bool = ...) -> None: ...

class SetChimeMuteResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetChimeVolumeRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "volume"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    volume: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., volume: _Optional[int] = ...) -> None: ...

class SetChimeVolumeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDetectionWindowsRequest(_message.Message):
    __slots__ = ["detection_windows", "device_id", "panel_id"]
    DETECTION_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    detection_windows: _containers.RepeatedCompositeFieldContainer[DetectionWindow]
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., detection_windows: _Optional[_Iterable[_Union[DetectionWindow, _Mapping]]] = ...) -> None: ...

class SetDetectionWindowsResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterAggressionLevelRequest(_message.Message):
    __slots__ = ["device_id", "level", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    level: DeterAggressionLevel
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., level: _Optional[_Union[DeterAggressionLevel, str]] = ...) -> None: ...

class SetDeterAggressionLevelResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterBoundaryRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id", "point_list"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_LIST_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    point_list: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., point_list: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetDeterBoundaryResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterLightColorRequest(_message.Message):
    __slots__ = ["color", "device_id", "panel_id"]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    color: DeterLightColor
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., color: _Optional[_Union[DeterLightColor, str]] = ...) -> None: ...

class SetDeterLightColorResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterLightPatternRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "pattern"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    pattern: DeterLightPattern
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., pattern: _Optional[_Union[DeterLightPattern, str]] = ...) -> None: ...

class SetDeterLightPatternResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterLightingBehaviorRequest(_message.Message):
    __slots__ = ["header", "lightingBehavior"]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    LIGHTINGBEHAVIOR_FIELD_NUMBER: _ClassVar[int]
    header: SettingsRequestHeader
    lightingBehavior: LightingBehavior
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., lightingBehavior: _Optional[_Union[LightingBehavior, _Mapping]] = ...) -> None: ...

class SetDeterLightingBehaviorResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterOverrideRequest(_message.Message):
    __slots__ = ["device_id", "enabled", "end_timestamp", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    enabled: bool
    end_timestamp: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., enabled: bool = ..., end_timestamp: _Optional[int] = ...) -> None: ...

class SetDeterOverrideResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterScheduleRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "schedule", "type"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    schedule: DeterSchedule
    type: DeterScheduleType
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., type: _Optional[_Union[DeterScheduleType, str]] = ..., schedule: _Optional[_Union[DeterSchedule, _Mapping]] = ...) -> None: ...

class SetDeterScheduleResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeterScheduleV2Request(_message.Message):
    __slots__ = ["device_id", "panel_id", "schedule_settings"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    schedule_settings: DeterScheduleSettingsV2
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., schedule_settings: _Optional[_Union[DeterScheduleSettingsV2, _Mapping]] = ...) -> None: ...

class SetDeterScheduleV2Response(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeviceNameRequest(_message.Message):
    __slots__ = ["device_id", "header", "name", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    name: str
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., name: _Optional[str] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetDeviceNameResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDeviceOnboardingRequest(_message.Message):
    __slots__ = ["analytics_opt_in", "camera_name", "camera_rotate", "deter_aggression_level", "deter_intro", "deter_schedule", "device_id", "doorbell_position", "header", "notifications", "package_delivery_locations", "package_watch", "panel_id", "property_boundary", "property_boundary_v2", "spotlight_analytics_opt_in", "spotlight_camera_name", "spotlight_default_settings", "spotlight_deter_intro", "spotlight_deter_schedule", "spotlight_onboarding_done", "spotlight_splash"]
    ANALYTICS_OPT_IN_FIELD_NUMBER: _ClassVar[int]
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ROTATE_FIELD_NUMBER: _ClassVar[int]
    DETER_AGGRESSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    DETER_INTRO_FIELD_NUMBER: _ClassVar[int]
    DETER_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DOORBELL_POSITION_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_DELIVERY_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_WATCH_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_BOUNDARY_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_BOUNDARY_V2_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_ANALYTICS_OPT_IN_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DEFAULT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DETER_INTRO_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_DETER_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_ONBOARDING_DONE_FIELD_NUMBER: _ClassVar[int]
    SPOTLIGHT_SPLASH_FIELD_NUMBER: _ClassVar[int]
    analytics_opt_in: bool
    camera_name: bool
    camera_rotate: bool
    deter_aggression_level: bool
    deter_intro: bool
    deter_schedule: bool
    device_id: int
    doorbell_position: bool
    header: SettingsRequestHeader
    notifications: bool
    package_delivery_locations: bool
    package_watch: bool
    panel_id: int
    property_boundary: bool
    property_boundary_v2: bool
    spotlight_analytics_opt_in: bool
    spotlight_camera_name: bool
    spotlight_default_settings: bool
    spotlight_deter_intro: bool
    spotlight_deter_schedule: bool
    spotlight_onboarding_done: bool
    spotlight_splash: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., property_boundary: bool = ..., notifications: bool = ..., deter_intro: bool = ..., deter_schedule: bool = ..., deter_aggression_level: bool = ..., camera_name: bool = ..., camera_rotate: bool = ..., analytics_opt_in: bool = ..., doorbell_position: bool = ..., package_delivery_locations: bool = ..., package_watch: bool = ..., property_boundary_v2: bool = ..., spotlight_splash: bool = ..., spotlight_deter_intro: bool = ..., spotlight_default_settings: bool = ..., spotlight_deter_schedule: bool = ..., spotlight_camera_name: bool = ..., spotlight_analytics_opt_in: bool = ..., spotlight_onboarding_done: bool = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetDeviceOnboardingResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDoorbellChimeRequest(_message.Message):
    __slots__ = ["chime", "device_id", "device_uuid", "header", "panel_id", "standalone_enabled"]
    CHIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_UUID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    STANDALONE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    chime: DoorbellChime
    device_id: int
    device_uuid: str
    header: SettingsRequestHeader
    panel_id: int
    standalone_enabled: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., chime: _Optional[_Union[DoorbellChime, str]] = ..., standalone_enabled: bool = ..., device_uuid: _Optional[str] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetDoorbellChimeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDoorbellMutedRequest(_message.Message):
    __slots__ = ["device_id", "muted", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MUTED_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    muted: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., muted: bool = ...) -> None: ...

class SetDoorbellMutedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDoorbellPositionRequest(_message.Message):
    __slots__ = ["device_id", "doorbell_position", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DOORBELL_POSITION_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    doorbell_position: DoorbellPosition
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., doorbell_position: _Optional[_Union[DoorbellPosition, str]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetDoorbellPositionResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetDynamicChimeRequest(_message.Message):
    __slots__ = ["chime_category_id", "chime_id", "chime_type", "device_id", "panel_id"]
    CHIME_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    CHIME_ID_FIELD_NUMBER: _ClassVar[int]
    CHIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    chime_category_id: str
    chime_id: str
    chime_type: ChimeType
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., chime_category_id: _Optional[str] = ..., chime_id: _Optional[str] = ..., chime_type: _Optional[_Union[ChimeType, str]] = ...) -> None: ...

class SetDynamicChimeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetExtendSirenRequest(_message.Message):
    __slots__ = ["device_id", "extend_siren", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    EXTEND_SIREN_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    extend_siren: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., extend_siren: bool = ...) -> None: ...

class SetExtendSirenResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetIRLEDRequest(_message.Message):
    __slots__ = ["device_id", "ir_led_on", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    IR_LED_ON_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    ir_led_on: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., ir_led_on: bool = ...) -> None: ...

class SetIRLEDResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetLingerDurationRequest(_message.Message):
    __slots__ = ["device_id", "duration", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    duration: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...

class SetLingerDurationResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetLurkerDeterRequest(_message.Message):
    __slots__ = ["device_id", "lurker_deter", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    LURKER_DETER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    lurker_deter: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., lurker_deter: bool = ...) -> None: ...

class SetLurkerDeterResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetMaintainZoomRequest(_message.Message):
    __slots__ = ["device_id", "maintain_zoom", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MAINTAIN_ZOOM_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    maintain_zoom: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., maintain_zoom: bool = ...) -> None: ...

class SetMaintainZoomResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetNightVisionRequest(_message.Message):
    __slots__ = ["device_id", "night_vision", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    NIGHT_VISION_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    night_vision: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., night_vision: bool = ...) -> None: ...

class SetNightVisionResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetNotifyOnRequest(_message.Message):
    __slots__ = ["device_id", "enabled", "header", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    enabled: bool
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., enabled: bool = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetNotifyOnResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPackageBoundaryRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id", "point_list"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_LIST_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    point_list: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., point_list: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetPackageBoundaryResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPackageChimeRequest(_message.Message):
    __slots__ = ["chime", "device_id", "header", "panel_id"]
    CHIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    chime: PackageChime
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., chime: _Optional[_Union[PackageChime, str]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetPackageChimeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPackageDeliveryLocationsRequest(_message.Message):
    __slots__ = ["device_id", "header", "package_delivery_locations", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_DELIVERY_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    package_delivery_locations: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPoint]
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., package_delivery_locations: _Optional[_Iterable[_Union[PropertyBoundaryPoint, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetPackageDeliveryLocationsResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPackageWatchRequest(_message.Message):
    __slots__ = ["device_id", "package_watch", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_WATCH_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    package_watch: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., package_watch: bool = ...) -> None: ...

class SetPackageWatchResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPackageWatchStateRequest(_message.Message):
    __slots__ = ["device_id", "end_timestamp", "on_duty", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ON_DUTY_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    end_timestamp: int
    on_duty: bool
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., on_duty: bool = ..., end_timestamp: _Optional[int] = ...) -> None: ...

class SetPackageWatchStateResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetPropertyBoundaryRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id", "point_list"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_LIST_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    point_list: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., point_list: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetPropertyBoundaryResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetQuietModeRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "quiet_mode"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    QUIET_MODE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    quiet_mode: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., quiet_mode: bool = ...) -> None: ...

class SetQuietModeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordForRegionsRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_for_region"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_FOR_REGION_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_for_region: RecordForRegions
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_for_region: _Optional[_Union[RecordForRegions, str]] = ...) -> None: ...

class SetRecordForRegionsResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnAnimalDetectedRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_animal"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_ANIMAL_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_animal: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_animal: bool = ...) -> None: ...

class SetRecordOnAnimalDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnDeterRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_deter"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_DETER_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_deter: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_deter: bool = ...) -> None: ...

class SetRecordOnDeterResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnLurkerDetectedRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_lurker"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_LURKER_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_lurker: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_lurker: bool = ...) -> None: ...

class SetRecordOnLurkerDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnPackageDetectedRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_package"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_PACKAGE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_package: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_package: bool = ...) -> None: ...

class SetRecordOnPackageDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnPersonDetectedRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_person"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_PERSON_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_person: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_person: bool = ...) -> None: ...

class SetRecordOnPersonDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRecordOnVehicleDetectedRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "record_on_vehicle"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_ON_VEHICLE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    record_on_vehicle: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., record_on_vehicle: bool = ...) -> None: ...

class SetRecordOnVehicleDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetRotateImageRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "rotate_image"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    ROTATE_IMAGE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    rotate_image: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., rotate_image: bool = ...) -> None: ...

class SetRotateImageResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSmartSentrySnoozeRequest(_message.Message):
    __slots__ = ["device_id", "duration", "panel_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    duration: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...

class SetSmartSentrySnoozeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightBrightnessRequest(_message.Message):
    __slots__ = ["brightness_percent", "header"]
    BRIGHTNESS_PERCENT_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    brightness_percent: float
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., brightness_percent: _Optional[float] = ...) -> None: ...

class SetSpotlightBrightnessResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightCalibrationRequest(_message.Message):
    __slots__ = ["calibration_data", "header"]
    CALIBRATION_DATA_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    calibration_data: SpotlightCalibrationData
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., calibration_data: _Optional[_Union[SpotlightCalibrationData, _Mapping]] = ...) -> None: ...

class SetSpotlightCalibrationResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightFollowRequest(_message.Message):
    __slots__ = ["follow", "header"]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    follow: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., follow: bool = ...) -> None: ...

class SetSpotlightFollowResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightLightOnPersonDetectedRequest(_message.Message):
    __slots__ = ["LightOnPersonDetected", "header"]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    LIGHTONPERSONDETECTED_FIELD_NUMBER: _ClassVar[int]
    LightOnPersonDetected: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., LightOnPersonDetected: bool = ...) -> None: ...

class SetSpotlightLightOnPersonDetectedResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightNightLightRequest(_message.Message):
    __slots__ = ["enabled", "header"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., enabled: bool = ...) -> None: ...

class SetSpotlightNightLightResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightOnSunsetToSunriseRequest(_message.Message):
    __slots__ = ["enabled", "header"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., enabled: bool = ...) -> None: ...

class SetSpotlightOnSunsetToSunriseResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetSpotlightZonesRequest(_message.Message):
    __slots__ = ["enabled_zones_bitfield", "header"]
    ENABLED_ZONES_BITFIELD_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    enabled_zones_bitfield: int
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., enabled_zones_bitfield: _Optional[int] = ...) -> None: ...

class SetSpotlightZonesResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetStatusLightRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "status_light"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_LIGHT_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    status_light: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., status_light: bool = ...) -> None: ...

class SetStatusLightResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetUseAsDoorbellChimeExtenderRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "use_as_doorbell_chime_extender"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    USE_AS_DOORBELL_CHIME_EXTENDER_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    use_as_doorbell_chime_extender: bool
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., use_as_doorbell_chime_extender: bool = ...) -> None: ...

class SetUseAsDoorbellChimeExtenderResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetUserRoleRequest(_message.Message):
    __slots__ = ["header", "newRole", "targetUserId"]
    class UserRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ADMIN: SetUserRoleRequest.UserRole
    HEADER_FIELD_NUMBER: _ClassVar[int]
    NEWROLE_FIELD_NUMBER: _ClassVar[int]
    NON_ADMIN: SetUserRoleRequest.UserRole
    NO_ROLE: SetUserRoleRequest.UserRole
    OWNER: SetUserRoleRequest.UserRole
    TARGETUSERID_FIELD_NUMBER: _ClassVar[int]
    header: SettingsRequestHeader
    newRole: SetUserRoleRequest.UserRole
    targetUserId: str
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., targetUserId: _Optional[str] = ..., newRole: _Optional[_Union[SetUserRoleRequest.UserRole, str]] = ...) -> None: ...

class SetUserRoleResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetVehicleBoundaryRequest(_message.Message):
    __slots__ = ["device_id", "header", "panel_id", "point_list"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_LIST_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    header: SettingsRequestHeader
    panel_id: int
    point_list: _containers.RepeatedCompositeFieldContainer[PropertyBoundaryPointList]
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., point_list: _Optional[_Iterable[_Union[PropertyBoundaryPointList, _Mapping]]] = ..., header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ...) -> None: ...

class SetVehicleBoundaryResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetVideoQualityRequest(_message.Message):
    __slots__ = ["device_id", "panel_id", "quality"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    panel_id: int
    quality: VideoQuality
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., quality: _Optional[_Union[VideoQuality, str]] = ...) -> None: ...

class SetVideoQualityResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SetVisitorChimeRequest(_message.Message):
    __slots__ = ["chime", "device_id", "panel_id"]
    CHIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    chime: VisitorChime
    device_id: int
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., device_id: _Optional[int] = ..., chime: _Optional[_Union[VisitorChime, str]] = ...) -> None: ...

class SetVisitorChimeResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SettingsRequestHeader(_message.Message):
    __slots__ = ["device_type", "device_uuid", "panel_device_id", "standalone_camera_id", "standalone_enabled"]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_UUID_FIELD_NUMBER: _ClassVar[int]
    PANEL_DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STANDALONE_CAMERA_ID_FIELD_NUMBER: _ClassVar[int]
    STANDALONE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    device_type: str
    device_uuid: str
    panel_device_id: PanelDeviceIds
    standalone_camera_id: StandaloneCameraIds
    standalone_enabled: bool
    def __init__(self, panel_device_id: _Optional[_Union[PanelDeviceIds, _Mapping]] = ..., device_uuid: _Optional[str] = ..., standalone_camera_id: _Optional[_Union[StandaloneCameraIds, _Mapping]] = ..., device_type: _Optional[str] = ..., standalone_enabled: bool = ...) -> None: ...

class SoftwareVersion(_message.Message):
    __slots__ = ["build", "maintenance", "major", "minor"]
    BUILD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_FIELD_NUMBER: _ClassVar[int]
    MAJOR_FIELD_NUMBER: _ClassVar[int]
    MINOR_FIELD_NUMBER: _ClassVar[int]
    build: int
    maintenance: int
    major: int
    minor: int
    def __init__(self, major: _Optional[int] = ..., minor: _Optional[int] = ..., maintenance: _Optional[int] = ..., build: _Optional[int] = ...) -> None: ...

class SpotlightCalibrationData(_message.Message):
    __slots__ = ["calibration_type", "zones"]
    class CalibrationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class ZoneData(_message.Message):
        __slots__ = ["in_fov", "x", "y", "zone_id"]
        IN_FOV_FIELD_NUMBER: _ClassVar[int]
        X_FIELD_NUMBER: _ClassVar[int]
        Y_FIELD_NUMBER: _ClassVar[int]
        ZONE_ID_FIELD_NUMBER: _ClassVar[int]
        in_fov: bool
        x: float
        y: float
        zone_id: int
        def __init__(self, zone_id: _Optional[int] = ..., x: _Optional[float] = ..., y: _Optional[float] = ..., in_fov: bool = ...) -> None: ...
    CALIBRATION_TYPE_AUTO: SpotlightCalibrationData.CalibrationType
    CALIBRATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_TYPE_MANUAL: SpotlightCalibrationData.CalibrationType
    ZONES_FIELD_NUMBER: _ClassVar[int]
    calibration_type: SpotlightCalibrationData.CalibrationType
    zones: _containers.RepeatedCompositeFieldContainer[SpotlightCalibrationData.ZoneData]
    def __init__(self, calibration_type: _Optional[_Union[SpotlightCalibrationData.CalibrationType, str]] = ..., zones: _Optional[_Iterable[_Union[SpotlightCalibrationData.ZoneData, _Mapping]]] = ...) -> None: ...

class StandaloneCameraIds(_message.Message):
    __slots__ = ["device_id", "device_uuid", "smarthomesystem_id"]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_UUID_FIELD_NUMBER: _ClassVar[int]
    SMARTHOMESYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    device_uuid: str
    smarthomesystem_id: int
    def __init__(self, smarthomesystem_id: _Optional[int] = ..., device_uuid: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class StartCameraWifiConnectRequest(_message.Message):
    __slots__ = ["camera_ap_ssids", "panel_id"]
    CAMERA_AP_SSIDS_FIELD_NUMBER: _ClassVar[int]
    PANEL_ID_FIELD_NUMBER: _ClassVar[int]
    camera_ap_ssids: _containers.RepeatedScalarFieldContainer[str]
    panel_id: int
    def __init__(self, panel_id: _Optional[int] = ..., camera_ap_ssids: _Optional[_Iterable[str]] = ...) -> None: ...

class StartCameraWifiConnectResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class SystemRequestHeader(_message.Message):
    __slots__ = ["is_smarthome_system", "system_id"]
    IS_SMARTHOME_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_ID_FIELD_NUMBER: _ClassVar[int]
    is_smarthome_system: bool
    system_id: int
    def __init__(self, system_id: _Optional[int] = ..., is_smarthome_system: bool = ...) -> None: ...

class TechnicalInfo(_message.Message):
    __slots__ = ["AP_SSID", "actual_type", "analytics_version", "audio_codec", "audio_sample_rate", "ip_address", "mac_address", "signal_strength", "software_version", "status"]
    class AudioCodec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ACTUAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    ANALYTICS_VERSION_FIELD_NUMBER: _ClassVar[int]
    AP_SSID: str
    AP_SSID_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CODEC_FIELD_NUMBER: _ClassVar[int]
    AUDIO_SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    INVALID: TechnicalInfo.AudioCodec
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MU_LAW_G_711: TechnicalInfo.AudioCodec
    OPUS: TechnicalInfo.AudioCodec
    SIGNAL_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    actual_type: str
    analytics_version: str
    audio_codec: TechnicalInfo.AudioCodec
    audio_sample_rate: int
    ip_address: str
    mac_address: str
    signal_strength: float
    software_version: str
    status: bool
    def __init__(self, status: bool = ..., signal_strength: _Optional[float] = ..., ip_address: _Optional[str] = ..., AP_SSID: _Optional[str] = ..., software_version: _Optional[str] = ..., analytics_version: _Optional[str] = ..., actual_type: _Optional[str] = ..., mac_address: _Optional[str] = ..., audio_codec: _Optional[_Union[TechnicalInfo.AudioCodec, str]] = ..., audio_sample_rate: _Optional[int] = ...) -> None: ...

class ToggleFloodlightRequest(_message.Message):
    __slots__ = ["floodlight_on", "header"]
    FLOODLIGHT_ON_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    floodlight_on: bool
    header: SettingsRequestHeader
    def __init__(self, header: _Optional[_Union[SettingsRequestHeader, _Mapping]] = ..., floodlight_on: bool = ...) -> None: ...

class ToggleFloodlightResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: Response
    def __init__(self, response: _Optional[_Union[Response, _Mapping]] = ...) -> None: ...

class TypeCapabilities(_message.Message):
    __slots__ = ["capabilities", "type"]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    capabilities: _containers.RepeatedScalarFieldContainer[int]
    type: int
    def __init__(self, type: _Optional[int] = ..., capabilities: _Optional[_Iterable[int]] = ...) -> None: ...

class DeterScheduleType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DeterAggressionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DeterLightColor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DeterLightPattern(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VideoQuality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DoorbellChime(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class VisitorChime(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class PackageChime(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class RecordForRegions(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class ChimeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class DoorbellPosition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SpotlightMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class SpotlightStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

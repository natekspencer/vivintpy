"""Module that implements the Camera class."""
import logging
from datetime import datetime

from ..const import CameraAttribute as Attribute
from ..const import PanelCredentialAttribute
from . import VivintDevice
from .alarm_panel import AlarmPanel

_LOGGER = logging.getLogger(__name__)

# Some Vivint supported cameras may be connected directly to your local network
# and the Vivint API reports these as having direct access availiable (cda).
# Ping cameras (alpha_cs6022_camera_device) can be setup to connect to your own
# Wi-Fi via a complicated process involving removing and resetting the camera,
# initiating WPS on your Wi-Fi and the Ping camera, and then adding a new camera
# from the panel within a limited timeframe. The Ping camera, however, seems to
# still have a VPN connection with the panel that prevents direct access except
# on very rare occasions. As such, we want to skip this model from direct access.
SKIP_DIRECT = ["alpha_cs6022_camera_device"]

DOORBELL_DING = "doorbell_ding"
MOTION_DETECTED = "motion_detected"
THUMBNAIL_READY = "thumbnail_ready"
VIDEO_READY = "video_ready"


class Camera(VivintDevice):
    """Represents a Vivint camera."""

    def __init__(self, data: dict, alarm_panel: AlarmPanel):
        """Initialize a camera."""
        super().__init__(data, alarm_panel)
        manufacturer_and_model = self.data.get(Attribute.ACTUAL_TYPE).split("_")[0:2]
        self._manufacturer = manufacturer_and_model[0].title()
        self._model = manufacturer_and_model[1].upper()

    @property
    def serial_number(self) -> str:
        """Return the camera's mac address as the serial number."""
        return self.mac_address

    @property
    def software_version(self) -> str:
        """Return the camera's software version."""
        return self.data.get(Attribute.SOFTWARE_VERSION)

    @property
    def capture_clip_on_motion(self) -> bool:
        """Return True if capture clip on motion is active."""
        return self.data[Attribute.CAPTURE_CLIP_ON_MOTION]

    @property
    def ip_address(self) -> str:
        """Camera's IP address."""
        return self.data[Attribute.CAMERA_IP_ADDRESS]

    @property
    def mac_address(self) -> str:
        """Camera's MAC Address."""
        return self.data[Attribute.CAMERA_MAC]

    @property
    def is_in_privacy_mode(self) -> bool:
        """Return True if privacy mode is active."""
        return self.data[Attribute.CAMERA_PRIVACY]

    @property
    def is_online(self) -> bool:
        """Return True if camera is online."""
        return self.data[Attribute.ONLINE]

    @property
    def wireless_signal_strength(self) -> int:
        """Camera's wireless signal strength."""
        return self.data[Attribute.WIRELESS_SIGNAL_STRENGTH]

    async def request_thumbnail(self) -> None:
        """Request a new thumbnail for the camera."""
        await self.vivintskyapi.request_camera_thumbnail(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id
        )

    async def get_thumbnail_url(self) -> str:
        """Return the latest camera thumbnail URL."""
        # Sometimes this date field comes back with a "Z" at the end
        # and sometimes it doesn't, so let's just safely remove it.
        camera_thumbnail_date = datetime.strptime(
            self.data[Attribute.CAMERA_THUMBNAIL_DATE].replace("Z", ""),
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        thumbnail_timestamp = int(camera_thumbnail_date.timestamp() * 1000)

        return await self.vivintskyapi.get_camera_thumbnail_url(
            self.alarm_panel.id,
            self.alarm_panel.partition_id,
            self.id,
            thumbnail_timestamp,
        )

    async def get_rtsp_url(self, internal: bool = False, hd: bool = False) -> str:
        """Return the rtsp URL for the camera."""
        credentials = await self.alarm_panel.get_panel_credentials()
        url = self.data[f"c{'i' if internal else 'e'}u{'' if hd else 's'}"][0]
        return f"{url[:7]}{credentials[PanelCredentialAttribute.NAME]}:{credentials[PanelCredentialAttribute.PASSWORD]}@{url[7:]}"

    async def get_direct_rtsp_url(self, hd: bool = False) -> str:
        """Return the direct rtsp url for this camera, in HD if requested, if any."""
        return (
            f"rtsp://{self.data[Attribute.USERNAME]}:{self.data[Attribute.PASSWORD]}@{self.ip_address}:{self.data[Attribute.CAMERA_IP_PORT]}/{self.data[Attribute.CAMERA_DIRECT_STREAM_PATH if hd else Attribute.CAMERA_DIRECT_STREAM_PATH_STANDARD]}"
            if self.data[Attribute.CAMERA_DIRECT_AVAILABLE]
            and self.data.get(Attribute.ACTUAL_TYPE) not in SKIP_DIRECT
            else None
        )

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message addressed to this camera."""
        super().handle_pubnub_message(message)

        event = None

        if message.get(Attribute.CAMERA_THUMBNAIL_DATE):
            event = THUMBNAIL_READY
        elif message.get(Attribute.DING_DONG):
            event = DOORBELL_DING
        elif message.keys() == set([Attribute.ID, Attribute.TYPE]):
            event = VIDEO_READY
        elif message.get(Attribute.VISITOR_DETECTED) or message.keys() in [
            set([Attribute.ID, Attribute.ACTUAL_TYPE, Attribute.STATE]),
            set([Attribute.ID, Attribute.DETER_ON_DUTY, Attribute.TYPE]),
        ]:
            event = MOTION_DETECTED

        if event is not None:
            self.emit(event, {"message": message})

        _LOGGER.debug("Message received by %s: %s", self.name, message)

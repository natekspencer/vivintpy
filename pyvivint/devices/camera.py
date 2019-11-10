"""Module that implements the Camera class."""
from datetime import datetime
from typing import Callable, List
from pyvivint.enums import CameraAttributes as Attributes
from pyvivint.devices import VivintDevice


class Camera(VivintDevice):
    """Represents a vivint camera device."""
    def __init__(self, data: dict, alarm_panel: 'pyvivint.devices.alarm_panel.AlarmPanel'):
        super().__init__(data, alarm_panel)
        self.__thumbnail_ready_callbacks: List[Callable] = list()

    @property
    def capture_clip_on_motion(self) -> bool:
        "Return True if capture clip on motion is active."
        return self.data[Attributes.CaptureClipOnMotion]

    @property
    def ip_address(self) -> str:
        "Camera's IP address."
        return self.data[Attributes.CameraIPAddress]

    @property
    def is_in_privacy_mode(self) -> bool:
        """Return True if privacy mode is active."""
        return self.data[Attributes.CameraPrivacy]

    @property
    def is_online(self) -> bool:
        """Return True if camera is online."""
        return self.data[Attributes.Online]

    @property
    def wireless_signal_strength(self) -> int:
        """Camera's wireless signal strength."""
        return self.data[Attributes.WirelessSignalStrenght]

    def add_thumbnail_ready_callback(self, callback: Callable) -> None:
        """Register a thumbnail_ready callback."""
        self.__thumbnail_ready_callbacks.append(callback)

    async def request_camera_thumbnail(self) -> None:
        """Request a new thumbnail for the camera."""
        await self.vivintskyapi.request_camera_thumbnail(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id
        )

    async def get_camera_thumbnail_url(self) -> str:
        """Returns the latest camera thumbnail URL."""
        camera_thumbnail_date = datetime.strptime(self.data[Attributes.CameraThumbnailDate], '%Y-%m-%dT%H:%M:%S.%fZ')
        thumbnail_timestamp = int(camera_thumbnail_date.timestamp() * 1000)

        return await self.vivintskyapi.get_camera_thumbnail_url(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, thumbnail_timestamp
        )

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message addressed to this camera."""
        super().handle_pubnub_message(message)

        if message.get(Attributes.CameraThumbnailDate):
            self._fire_callbacks(self.__thumbnail_ready_callbacks)

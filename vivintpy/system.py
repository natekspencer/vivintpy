"""Module that implements the System class."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from aiohttp import ClientError

from .api import VivintSkyApi
from .const import HistoryAttribute, PubNubMessageAttribute
from .const import SystemAttribute as Attribute
from .devices.alarm_panel import AlarmPanel
from .entity import Entity
from .enums import ArmedState
from .exceptions import VivintError
from .spacemonkey import SpaceMonkeyDvr, find_dvr_service_id
from .user import User
from .utils import first_or_none

_LOGGER = logging.getLogger(__name__)

# What Vivint reports for anything at the panel that it doesn't name a user for
CHANGED_BY_PANEL = "panel"
# History icons for the states that are recorded there. Exit delays aren't recorded
# until they finish, when another event is sent with the armed state.
HISTORY_ICONS = {
    ArmedState.DISARMED: "disarmed",
    ArmedState.ARMED_STAY: "armed_stay",
    ArmedState.ARMED_AWAY: "armed_away",
}
HISTORY_RETRY_DELAYS = (0.5, 1, 2, 4)
HISTORY_TIME_TOLERANCE = timedelta(seconds=5)


class System(Entity):
    """Describe a vivint system."""

    def __init__(self, data: dict, api: VivintSkyApi, *, name: str, is_admin: bool):
        """Initialize a system."""
        super().__init__(data)
        self._api = api
        self._name = name
        self._is_admin = is_admin
        self.__changed_by_lookup: asyncio.Task | None = None
        self.alarm_panels: list[AlarmPanel] = [
            AlarmPanel(panel_data, self)
            for panel_data in self.data[Attribute.SYSTEM][Attribute.PARTITION]
        ]
        self.users = [
            User(user_data, self)
            for user_data in self.data[Attribute.SYSTEM][Attribute.USERS]
        ]
        self._dvr = SpaceMonkeyDvr.from_system_data(api, data)
        self._stale_dvrs: list[SpaceMonkeyDvr] = []

    @property
    def dvr(self) -> SpaceMonkeyDvr | None:
        """Return the DVR that stores this system's recordings, if there is one."""
        return self._dvr

    @property
    def api(self) -> VivintSkyApi:
        """Return the API."""
        return self._api

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """System's id."""
        return int(self.data[Attribute.SYSTEM][Attribute.PANEL_ID])

    @property
    def is_admin(self) -> bool:
        """Return True if the user is an admin for this system."""
        return self._is_admin

    @property
    def name(self) -> str:
        """System's name."""
        return self._name

    async def refresh(self) -> None:
        """Reload a system's data from the VivintSky API."""
        system_data = await self.api.get_system_data(self.id)
        self._refresh_dvr(system_data)

        for panel_data in system_data[Attribute.SYSTEM][Attribute.PARTITION]:
            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel, panel_data=panel_data: (  # type: ignore
                    panel.id == panel_data[Attribute.PANEL_ID]
                    and panel.partition_id == panel_data[Attribute.PARTITION_ID]
                ),
            )
            if alarm_panel:
                alarm_panel.refresh(panel_data)
            else:
                self.alarm_panels.append(AlarmPanel(panel_data, self))

        await self._close_stale_dvrs()

    def _refresh_dvr(self, system_data: dict) -> None:
        """Create, replace or drop the DVR when the system's DVR service changed."""
        service_id = find_dvr_service_id(system_data)
        if self._dvr and self._dvr.dvr_service_id == service_id:
            return
        if self._dvr:
            self._stale_dvrs.append(self._dvr)
        self._dvr = SpaceMonkeyDvr.from_system_data(self.api, system_data)

    async def _close_stale_dvrs(self) -> None:
        """Close replaced DVRs, keeping any that fail so the next refresh retries."""
        batch, self._stale_dvrs = self._stale_dvrs, []
        self._stale_dvrs.extend(await self._disconnect_dvrs(batch))

    async def disconnect_dvrs(self) -> None:
        """Disconnect the DVR, and any replaced DVR that could not be closed before."""
        if self._dvr and self._dvr not in self._stale_dvrs:
            self._stale_dvrs.append(self._dvr)
        await self._close_stale_dvrs()

    @staticmethod
    async def _disconnect_dvrs(dvrs: list[SpaceMonkeyDvr]) -> list[SpaceMonkeyDvr]:
        """Disconnect the DVRs and return the ones that failed."""
        results = await asyncio.gather(
            *(dvr.disconnect() for dvr in dvrs), return_exceptions=True
        )
        failed: list[SpaceMonkeyDvr] = []
        for dvr, result in zip(dvrs, results, strict=True):
            if isinstance(result, BaseException):
                _LOGGER.debug("Error disconnecting from a DVR: %s", result)
                failed.append(dvr)
        return failed

    def update_user_data(self, data: list[dict]) -> None:
        """Update user data."""
        for d in data:

            def _matches(user: User, _id: str = d["_id"]) -> bool:
                return user.id == _id

            user = first_or_none(self.users, _matches)
            if not user:
                _LOGGER.debug("User not found for system %s: %s", self.id, d)
                return
            user.handle_pubnub_message(d)

    def __update_changed_by(self, data: dict) -> None:
        """
        Update the alarm panels with what armed or disarmed the system.

        These events are sent for the system rather than a partition, so they go to
        the panels in the event's state. They can arrive before the panel's own state
        update, so they go to every panel if none match.

        The history is then checked for Vivint's description of the event, and for the
        name of a key fob or other device that's only reported as the panel. Any newer
        event replaces that lookup.
        """
        for key in (Attribute.SECURITY_ARMED, Attribute.SECURITY_DISARMED):
            if not isinstance(event := data.get(key), dict):
                continue
            state = event.get(Attribute.SECURITY_STATE)
            panels = [panel for panel in self.alarm_panels if panel.state == state]
            panels = panels or self.alarm_panels
            for panel in panels:
                panel.update_changed_by(event.get(Attribute.SECURITY_NAME))
            self.cancel_changed_by_lookup()
            if state in HISTORY_ICONS and event.get(Attribute.SECURITY_TIMESTAMP):
                self.__changed_by_lookup = asyncio.create_task(
                    self.__look_up_changed_by(event, panels)
                )

    def cancel_changed_by_lookup(self) -> None:
        """Cancel any history lookup for what armed or disarmed the system."""
        if self.__changed_by_lookup:
            self.__changed_by_lookup.cancel()
            self.__changed_by_lookup = None

    async def __look_up_changed_by(self, event: dict, panels: list[AlarmPanel]) -> None:
        """Update the panels with what the history has for an event."""
        changed_by = event.get(Attribute.SECURITY_NAME)
        is_device = changed_by == CHANGED_BY_PANEL and not event.get(
            Attribute.SECURITY_USER_ID
        )
        for delay in HISTORY_RETRY_DELAYS:
            await asyncio.sleep(delay)
            try:
                history = await self.api.get_history(self.id)
            except (VivintError, ClientError, TimeoutError, ValueError) as err:
                _LOGGER.debug("Unable to get the history for %s: %s", self.id, err)
                return
            if (match := _find_history_event(event, history)) is not None:
                # The panel's own state update can arrive after the history has this
                # event. If it has moved on instead, the retries just run out.
                state = event.get(Attribute.SECURITY_STATE)
                in_state = [panel for panel in panels if panel.state == state]
                if not in_state:
                    continue
                context = match.get(HistoryAttribute.PANEL_CONTEXT) or {}
                device_name = context.get(HistoryAttribute.DEVICE_NAME)
                for panel in in_state:
                    panel.update_changed_by(
                        device_name if is_device and device_name else changed_by,
                        match.get(HistoryAttribute.MESSAGE),
                    )
                return

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message."""
        if (message_type := message[PubNubMessageAttribute.TYPE]) == "account_system":
            # this is a system message
            operation = message.get(PubNubMessageAttribute.OPERATION)
            data = message.get(PubNubMessageAttribute.DATA)

            if data and operation == "u":
                if Attribute.USERS in data:
                    self.update_user_data(data[Attribute.USERS])
                    del data[Attribute.USERS]
                self.update_data(data)
                self.__update_changed_by(data)

        elif message_type == "account_partition":
            # this is a message for one of the devices attached to this system
            partition_id = message.get(PubNubMessageAttribute.PARTITION_ID)
            if not partition_id:
                _LOGGER.debug(
                    "Ignoring account partition message (no partition id specified for system %s): %s",
                    self.id,
                    message,
                )
                return

            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel: (
                    panel.id == self.id and panel.partition_id == partition_id
                ),
            )

            if not alarm_panel:
                _LOGGER.debug(
                    "No alarm panel found for system %s, partition %s",
                    self.id,
                    partition_id,
                )
                return

            alarm_panel.handle_pubnub_message(message)
        elif message_type == "adaptive_home_settings":
            # Smart Comfort's home or away state, which nothing uses yet
            _LOGGER.debug(
                "Ignoring adaptive home settings for system %s: %s", self.id, message
            )
        else:
            _LOGGER.warning(
                "Unknown message received by system %s: %s", self.id, message
            )


def _find_history_event(event: dict, history: list[dict]) -> dict | None:
    """Return the history event for an armed or disarmed event, if it's there."""
    icon = HISTORY_ICONS[event[Attribute.SECURITY_STATE]]
    timestamp = _parse_timestamp(event[Attribute.SECURITY_TIMESTAMP])
    if timestamp is None:
        return None
    for item in history:
        item_timestamp = _parse_timestamp(item.get(HistoryAttribute.TIMESTAMP))
        if (
            item.get(HistoryAttribute.ICON) == icon
            and item_timestamp is not None
            and abs(item_timestamp - timestamp) <= HISTORY_TIME_TOLERANCE
        ):
            return item
    return None


def _parse_timestamp(value: str | None) -> datetime | None:
    """Return a timestamp from Vivint, or None if it isn't valid."""
    try:
        return datetime.fromisoformat(value or "")
    except ValueError:
        _LOGGER.debug("Ignoring an invalid timestamp: %s", value)
        return None

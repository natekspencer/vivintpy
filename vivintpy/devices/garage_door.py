"""Module that implements the GarageDoor class."""

from __future__ import annotations

import logging
from typing import Any

import grpc

from ..const import ZWaveDeviceAttribute as Attribute
from ..enums import GarageDoorState
from ..exceptions import VivintSkyGrpcError
from . import VivintDevice

_LOGGER = logging.getLogger(__name__)


class GarageDoor(VivintDevice):
    """Represents a vivint garage door device."""

    @property
    def is_closed(self) -> bool | None:
        """Return True if garage dooor is closed and None if unknown."""
        if self.state == GarageDoorState.UNKNOWN:
            return None
        return self.state == GarageDoorState.CLOSED

    @property
    def is_closing(self) -> bool:
        """Return True if garage dooor is closing."""
        return self.state == GarageDoorState.CLOSING

    @property
    def is_online(self) -> bool:
        """Return True if switch is online."""
        return bool(self.data[Attribute.ONLINE])

    @property
    def is_opening(self) -> bool:
        """Return True if garage dooor is opening."""
        return self.state == GarageDoorState.OPENING

    @property
    def state(self) -> GarageDoorState:
        """Return the garage door's state."""
        return GarageDoorState(self.data.get(Attribute.STATE))  # type: ignore

    def get_state(self) -> Any:
        """Return the garage door's state."""
        return self.data[Attribute.STATE]

    async def set_state(self, state: int) -> None:
        """Set garage door's state.

        Opening and closing go through the garage service, which replaced the
        door endpoint that now fails with a server error, and use that endpoint
        only when the service doesn't support the request.
        """
        assert self.alarm_panel
        panel_id = self.alarm_panel.id
        command = {
            GarageDoorState.OPENING: self.api.open_garage_door,
            GarageDoorState.CLOSING: self.api.close_garage_door,
        }.get(GarageDoorState(state))
        if command:
            try:
                await command(panel_id, self.id)
                return
            except VivintSkyGrpcError as err:
                if err.code != grpc.StatusCode.UNIMPLEMENTED:
                    raise
                _LOGGER.debug(
                    "%s isn't supported for garage door %s, using the door endpoint",
                    err.method,
                    self.id,
                )
        await self.api.set_garage_door_state(
            panel_id, self.alarm_panel.partition_id, self.id, state
        )

    async def close(self) -> None:
        """Close the garage door."""
        await self.set_state(GarageDoorState.CLOSING)

    async def open(self) -> None:
        """Open the garage door."""
        await self.set_state(GarageDoorState.OPENING)

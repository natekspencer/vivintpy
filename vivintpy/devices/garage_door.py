"""Module that implements the GarageDoor class."""
from __future__ import annotations

from typing import Any

from ..const import ZWaveDeviceAttribute as Attributes
from ..enums import GarageDoorState
from . import VivintDevice


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
    def is_opening(self) -> bool:
        """Return True if garage dooor is opening."""
        return self.state == GarageDoorState.OPENING

    @property
    def node_online(self) -> bool:
        """Return True if the node is online."""
        return bool(self.data[Attributes.ONLINE])

    @property
    def state(self) -> GarageDoorState:
        """Return the garage door's state."""
        return GarageDoorState(self.data.get(Attributes.STATE))  # type: ignore

    def get_state(self) -> Any:
        """Return the garage door's state."""
        return self.data[Attributes.STATE]

    async def set_state(self, state: int) -> None:
        """Set garage door's state."""
        assert self.alarm_panel
        await self.vivintskyapi.set_garage_door_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, state
        )

    async def close(self) -> None:
        """Close the garage door."""
        await self.set_state(GarageDoorState.CLOSING)

    async def open(self) -> None:
        """Open the garage door."""
        await self.set_state(GarageDoorState.OPENING)

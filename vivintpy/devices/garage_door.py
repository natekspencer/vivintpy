"""Module that implements the GarageDoor class."""

from __future__ import annotations

import logging
from typing import Any

import grpc

from ..api import garage_vendor_device_id
from ..const import ZWaveDeviceAttribute as Attribute
from ..enums import GarageDoorState
from ..exceptions import VivintSkyApiError, VivintSkyGrpcError
from . import VivintDevice

_LOGGER = logging.getLogger(__name__)


class GarageDoor(VivintDevice):
    """Represents a vivint garage door device."""

    # the garage service's id for this door, once looked up
    _service_id: str | None = None

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
                await command(panel_id, await self._vendor_device_id(panel_id))
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

    async def _vendor_device_id(self, panel_id: int) -> str:
        """Return the garage service's id for this door.

        The service lists each door with its own id. A panel door's id is built
        from the panel and device ids, but a door linked from another service,
        such as myQ, can use a different one, so the door is matched by its
        device id and then by its name.

        A matched id is kept for later commands. It's made of the panel and
        device ids, which don't change for this door.
        """
        if self._service_id is None:
            self._service_id = await self._find_vendor_device_id(panel_id)
        return self._service_id

    async def _find_vendor_device_id(self, panel_id: int) -> str:
        """Look up this door's id in the garage service's list of doors."""
        doors = await self.api.get_garage_doors(panel_id)
        _LOGGER.debug(
            "Garage service lists %s",
            [(door.vendor_device_id, door.name) for door in doors] or "no doors",
        )
        ids = [door.vendor_device_id for door in doors]
        if (expected := garage_vendor_device_id(panel_id, self.id)) in ids:
            return expected
        suffix = f":{self.id}"
        if len(matches := [i for i in ids if i.endswith(suffix)]) == 1:
            return matches[0]
        name = (self.name or "").strip().casefold()
        named = [d for d in doors if name and d.name.strip().casefold() == name]
        if len(named) == 1:
            return named[0].vendor_device_id
        raise VivintSkyApiError(
            f"The garage service doesn't list a door matching {self.name} ({self.id})"
        )

    async def close(self) -> None:
        """Close the garage door."""
        await self.set_state(GarageDoorState.CLOSING)

    async def open(self) -> None:
        """Open the garage door."""
        await self.set_state(GarageDoorState.OPENING)

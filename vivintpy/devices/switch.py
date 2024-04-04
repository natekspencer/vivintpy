"""Module that implements the Switch class."""

from __future__ import annotations

from ..const import SwitchAttribute as Attribute
from ..utils import send_deprecation_warning
from . import VivintDevice


class Switch(VivintDevice):
    """Represents a Vivint switch device."""

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return bool(self.data[Attribute.STATE])

    @property
    def is_online(self) -> bool:
        """Return True if switch is online."""
        return bool(self.data[Attribute.ONLINE])

    @property
    def level(self) -> int:
        """Return the level of the switch betwen 0..100."""
        return int(self.data[Attribute.VALUE])

    @property
    def node_online(self) -> bool:
        """Return True if the node is online."""
        send_deprecation_warning("node_online", "is_online")
        return self.is_online

    async def set_state(
        self,
        on: bool | None = None,  # pylint: disable=invalid-name
        level: int | None = None,
    ) -> None:
        """Set switch's state."""
        assert self.alarm_panel
        await self.api.set_switch_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, on, level
        )

    async def turn_on(self) -> None:
        """Turn on the switch."""
        await self.set_state(on=True)

    async def turn_off(self) -> None:
        """Turn off the switch."""
        await self.set_state(on=False)


class BinarySwitch(Switch):
    """Represents a Vivint binary switch device."""


class MultilevelSwitch(Switch):
    """Represents a Vivint multilevel switch device."""

    async def set_level(self, level: int) -> None:
        """Set the level of the switch between 0..100."""
        await self.set_state(level=level)

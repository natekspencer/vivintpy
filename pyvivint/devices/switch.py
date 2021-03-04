"""Module that implements the Switch class."""
from typing import Optional

from ..const import SwitchAttribute, ZWaveDeviceAttribute
from . import VivintDevice


class Switch(VivintDevice):
    """Represents a Vivint switch device."""

    @property
    def is_on(self) -> bool:
        """Returns True if switch is on."""
        return self.data[SwitchAttribute.STATE]

    @property
    def level(self) -> int:
        """Returns the level of the switch betwen 0..100."""
        return self.data[SwitchAttribute.VALUE]

    @property
    def node_online(self) -> bool:
        """Returns True if the node is online."""
        return self.data[ZWaveDeviceAttribute.ONLINE]

    async def set_state(
        self, on: Optional[bool] = None, level: Optional[int] = None
    ) -> None:
        """Set switch's state."""
        await self.vivintskyapi.set_switch_state(
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

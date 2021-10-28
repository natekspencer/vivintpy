"""Module that implements the DoorLock class."""
from ..const import ZWaveDeviceAttribute as Attributes
from . import BypassTamperDevice, VivintDevice


class DoorLock(BypassTamperDevice, VivintDevice):
    """Represents a vivint door lock device."""

    @property
    def battery_level(self) -> int:
        """Door lock's battery level."""
        return self.data[Attributes.BATTERY_LEVEL]

    @property
    def low_battery(self) -> bool:
        """Return True if battery level is low."""
        return self.data[Attributes.LOW_BATTERY]

    @property
    def is_locked(self) -> bool:
        """Return True if door lock is locked."""
        return self.data[Attributes.STATE]

    @property
    def node_online(self) -> bool:
        """Return True if the node is online."""
        return self.data[Attributes.ONLINE]

    async def set_state(self, locked: bool) -> None:
        """Set door lock's state."""
        await self.vivintskyapi.set_lock_state(
            self.alarm_panel.id, self.alarm_panel.partition_id, self.id, locked
        )

    async def lock(self) -> None:
        """Lock the door lock."""
        await self.set_state(True)

    async def unlock(self) -> None:
        """Unlock the door lock."""
        await self.set_state(False)

"""Module that implements the User class."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .const import UserAttribute as Attribute
from .entity import Entity

if TYPE_CHECKING:
    from .system import System

ADD_LOCK = f"{Attribute.LOCK_IDS}.1"


class User(Entity):
    """Describe a Vivint user."""

    def __init__(self, data: dict, system: System):
        """Initialize a user."""
        super().__init__(data)
        self._system = system

    def __repr__(self) -> str:
        """Return custom __repr__ of user."""
        return f"<{self.__class__.__name__} {self.id}, {self.name}{' (admin)' if self.is_admin else ''}>"

    @property
    def has_lock_pin(self) -> bool:
        """Return True if the user has pins."""
        return bool(self.data[Attribute.HAS_LOCK_PIN])

    @property
    def has_panel_pin(self) -> bool:
        """Return True if the user has pins."""
        return bool(self.data[Attribute.HAS_PANEL_PIN])

    @property
    def has_pins(self) -> bool:
        """Return True if the user has pins."""
        return bool(self.data[Attribute.HAS_PINS])

    @property
    def has_remote_access(self) -> bool:
        """Return True if the user has remote access."""
        return bool(self.data[Attribute.REMOTE_ACCESS])

    @property
    def id(self) -> int:  # pylint: disable=invalid-name
        """User's id."""
        return int(self.data[Attribute.ID])

    @property
    def is_admin(self) -> bool:
        """Return True if the user is an admin."""
        return bool(self.data[Attribute.ADMIN])

    @property
    def is_registered(self) -> bool:
        """Return True if the user is registered."""
        return bool(self.data[Attribute.REGISTERED])

    @property
    def lock_ids(self) -> list[int]:
        """User's lock ids."""
        return cast(list[int], self.data.get(Attribute.LOCK_IDS, []))

    @property
    def name(self) -> str:
        """User's name."""
        return str(self.data[Attribute.NAME])

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message addressed to this user."""
        if ADD_LOCK in message:
            message[Attribute.LOCK_IDS] = self.lock_ids + [message[ADD_LOCK]]
            del message[ADD_LOCK]
        super().handle_pubnub_message(message)

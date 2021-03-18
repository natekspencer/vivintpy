"""Module that implements the Entity class."""
from typing import Callable, Dict, List

from .utils import send_deprecation_warning

UPDATE = "update"


class Entity:
    """Describe a Vivint entity."""

    def __init__(self, data: dict):
        self.__data = data
        self._listeners: Dict[str, List[Callable]] = {}

    @property
    def data(self) -> dict:
        """Return entity's raw data as returned by VivintSky API."""
        return self.__data

    def update_data(self, new_val: dict, override: bool = False) -> None:
        """Update entity's raw data."""
        if override:
            self.__data = new_val
        else:
            self.__data.update(new_val)

        self.emit(UPDATE, {"data": new_val})

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message directed to this entity."""
        self.update_data(message)

    def add_update_callback(self, callback: Callable) -> None:
        """.. deprecated::

        (deprecated) Use `on("update", callback)` instead.
        """
        send_deprecation_warning(
            "add_update_callback(callback)", "on('update', callback)"
        )
        self.on(UPDATE, callback)

    def on(self, event_name: str, callback: Callable) -> Callable:
        """Register an event callback."""
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def emit(self, event_name: str, data: dict) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            listener(data)

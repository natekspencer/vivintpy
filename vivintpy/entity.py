"""Module that implements the Entity class."""

from __future__ import annotations

from collections.abc import Callable

UPDATE = "update"


class Entity:
    """Describe a Vivint entity."""

    def __init__(self, data: dict):
        """Initialize an entity."""
        self.__data = data
        self._listeners: dict[str, list[Callable]] = {}

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
        """Handle a pubnub message directed to this entity."""
        self.update_data(message)

    def on(  # pylint: disable=invalid-name
        self, event_name: str, callback: Callable
    ) -> Callable:
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
            try:
                listener(data)
            except:  # noqa E722 # pylint: disable=bare-except
                pass

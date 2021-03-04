"""Module that implements the Entity class."""
import logging
from typing import Callable, List

from .utils import add_async_job

_LOGGER = logging.getLogger(__name__)


class Entity:
    """Describe a vivint entity."""

    def __init__(self, data: dict):
        self.__data = data
        self.__update_callbacks: Callable = list()

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

        self._fire_callbacks(self.__update_callbacks)

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message directed to this entity."""
        self.update_data(message)

    def add_update_callback(self, callback: Callable) -> None:
        """Registers an update callback."""
        self.__update_callbacks.append(callback)

    def _fire_callbacks(self, callbacks: List[Callable], *args, **kwargs) -> None:
        """Execute callbacks.

        Handles both sync and async callbacks.
        """
        for callback in callbacks:
            try:
                add_async_job(callback)
            except Exception:
                _LOGGER.exception(
                    f"failed to execute callback for entity {self.__repr__()}"
                )

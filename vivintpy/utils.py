"""Utilities module."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Iterable, TypeVar
from warnings import warn

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")


def first_or_none(lst: Iterable[_T], predicate: Callable[[_T], Any]) -> _T | None:
    """Return the first occurrence or `None` of an iterable, given a predicate."""
    filter_iter = filter(predicate, lst)
    return next(filter_iter, None)


def add_async_job(target: Callable, *args):
    """Add a callable to the event loop."""
    loop = asyncio.get_event_loop()

    if asyncio.iscoroutine(target):
        task = loop.create_task(target)
    elif asyncio.iscoroutinefunction(target):
        task = loop.create_task(target(*args))
    else:
        task = loop.run_in_executor(None, target, *args)

    return task


def send_deprecation_warning(old_name: str, new_name: str) -> None:
    """Send a deprecation warning."""
    message = f"{old_name} has been deprecated in favor of {new_name}, the alias will be removed in the future"
    warn(
        message,
        DeprecationWarning,
        stacklevel=2,
    )
    _LOGGER.warning(message)

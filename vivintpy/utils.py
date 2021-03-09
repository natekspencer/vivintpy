"""Utilities module."""
import asyncio
import logging
from typing import Callable
from warnings import warn

_LOGGER = logging.getLogger(__name__)


def first_or_none(lst, predicate):
    filter_iter = filter(predicate, lst)
    return next(filter_iter, None)


def add_async_job(target: Callable, *args):
    loop = asyncio.get_event_loop()

    if asyncio.iscoroutine(target):
        task = loop.create_task(target)
    elif asyncio.iscoroutinefunction(target):
        task = loop.create_task(target(*args))
    else:
        task = loop.run_in_executor(None, target, *args)

    return task


def send_deprecation_warning(old_name, new_name):
    message = f"{old_name} has been deprecated in favor of {new_name}, the alias will be removed in the future"
    warn(
        message,
        DeprecationWarning,
        stacklevel=2,
    )
    _LOGGER.warn(message)

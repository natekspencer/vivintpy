"""Utilities module."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import os
import re
from typing import Any, Callable, Coroutine, Iterable, TypeVar
from warnings import warn

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")


def first_or_none(lst: Iterable[_T], predicate: Callable[[_T], Any]) -> _T | None:
    """Return the first occurrence or `None` of an iterable, given a predicate."""
    filter_iter = filter(predicate, lst)
    return next(filter_iter, None)


def add_async_job(
    target: Callable | Coroutine, *args: Any
) -> asyncio.Task | asyncio.Future:
    """Add a callable to the event loop."""
    loop = asyncio.get_event_loop()
    task: asyncio.Future | asyncio.Task

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


def generate_code_challenge() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge for authentication."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    code_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_hash).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    return (code_verifier, code_challenge)


def generate_state() -> str:
    """Generate state."""
    return base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")

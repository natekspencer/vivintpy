"""Module that implements the VivintPubNubSubscribeListener class."""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any

from pubnub.callbacks import SubscribeCallback
from pubnub.models.consumer.common import PNStatus
from pubnub.models.consumer.pubsub import PNMessageResult
from pubnub.pubnub_asyncio import PubNubAsyncio

PN_SUBSCRIBE_KEY = "sub-c-6fb03d68-6a78-11e2-ae8f-12313f022c90"
PN_CHANNEL = "PlatformChannel"

_LOGGER = logging.getLogger(__name__)


class VivintPubNubSubscribeListener(SubscribeCallback):
    """PubNub Subscribe Listener."""

    def __init__(self, message_received_callback: Callable):
        """Initialize the PubNub subscription."""
        super().__init__()
        self.__message_received_callback = message_received_callback

    def presence(self, pubnub: PubNubAsyncio, presence: Any) -> None:
        """Handle presence update."""
        _LOGGER.debug("Recieved new presence: %s", presence)

    def status(
        self,
        pubnub: PubNubAsyncio,
        status: PNStatus,
    ) -> None:
        """Handle a status update."""
        operation = op.name if isinstance(op := status.operation, Enum) else op
        category = cat.name if isinstance(cat := status.category, Enum) else cat
        if status.is_error():
            _LOGGER.error(
                "PubNub status error - operation: %s, category: %s, error: %s",
                operation,
                category,
                status.error_data.information,
            )
        else:
            _LOGGER.debug(
                "PubNub status update - operation: %s, category: %s",
                operation,
                category,
            )

    def message(
        self,
        pubnub: PubNubAsyncio,
        message: PNMessageResult,
    ) -> None:
        """Handle a message received."""
        self.__message_received_callback(message.message)

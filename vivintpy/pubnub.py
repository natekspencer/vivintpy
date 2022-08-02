"""Module that implements the VivintPubNubSubscribeListener class."""
from __future__ import annotations

import logging
from collections.abc import Callable
from enum import IntEnum, unique
from typing import Any

from pubnub.callbacks import SubscribeCallback
from pubnub.models.consumer.pubsub import PNMessageResult
from pubnub.pubnub_asyncio import PubNubAsyncio

from .pubnub_patches import PNStatus

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
        operation = PubNubOperationType(status.operation).name
        category = PubNubStatusCategory(status.category).name
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


@unique
class PubNubStatusCategory(IntEnum):
    """PubNub status category."""

    UNKNOWN = 1
    ACKNOWLEDGMENT = 2
    ACCESS_DENIED = 3
    TIMEOUT = 4
    NETWORK_ISSUES = 5
    CONNECTED = 6
    RECONNECTED = 7
    DISCONNECTED = 8
    UNEXPECTED_DISCONNECT = 9
    CANCELLED = 10
    BAD_REQUEST = 11
    MALFORMED_FILTER_EXPRESSION = 12
    MALFORMED_RESPONSE = 13
    DECRYPTION_ERROR = 14
    TLS_CONNECTION_FAILED = 15
    TLS_UNTRUSTED_CERTIFICATE = 16
    INTERNAL_EXCEPTION = 17

    # Handle unknown/future status category
    UNEXPECTED_STATUS_CATEGORY = -1

    @classmethod
    def _missing_(cls, value: Any) -> PubNubStatusCategory:
        if value is not None:
            _LOGGER.error("Unexpected status category value: %s", value)
        return cls.UNEXPECTED_STATUS_CATEGORY


@unique
class PubNubOperationType(IntEnum):
    """PubNub operation type."""

    SUBSCRIBE = 1
    UNSUBSCRIBE = 2
    PUBLISH = 3
    HISTORY = 4
    WHERE_NOW = 5

    HEARTBEAT = 6
    SET_STATE = 7
    ADD_CHANNELS_TO_GROUP = 8
    REMOVE_CHANNELS_FROM_GROUP = 9
    CHANNEL_GROUPS = 10
    REMOVE_GROUP = 11
    CHANNELS_FOR_GROUP = 12
    PUSH_NOTIFICATION_ENABLED_CHANNELS = 13
    ADD_PUSH_NOTIFICATIONS_ON_CHANNELS = 14
    REMOVE_PUSH_NOTIFICATIONS_FROM_CHANNELS = 15
    REMOVE_ALL_PUSH_NOTIFICATIONS = 16
    TIME = 17

    HERE_NOW = 18
    GET_STATE = 19
    ACCESS_MANAGER_AUDIT = 20
    ACCESS_MANAGER_GRANT = 21
    ACCESS_MANAGER_REVOKE = 22
    HISTORY_DELETE = 23
    MESSAGE_COUNT = 24
    FIRE = 25
    SIGNAL = 26

    ACCESS_MANAGER_REVOKE_TOKEN = 40
    ACCESS_MANAGER_GRANT_TOKEN = 41

    ADD_MESSAGE_ACTION = 42
    GET_MESSAGE_ACTIONS = 43
    DELETE_MESSAGE_ACTION = 44
    FETCH_MESSAGES = 45

    GET_FILES_ACTION = 46
    DELETE_FILE = 47
    GET_FILE_DOWNLOAD_URL_ACTION = 48
    FETCH_FILE_UPLOAD_S3_DATA_ACTION = 49
    DOWNLOAD_FILE_ACTION = 50
    SEND_FILE_ACTION = 51
    SEND_FILE_NOTIFICATION = 52

    SET_UUID_METADATA = 53
    GET_UUID_METADATA = 54
    REMOVE_UUID_METADATA = 55
    GET_ALL_UUID_METADATA = 56

    SET_CHANNEL_METADATA = 57
    GET_CHANNEL_METADATA = 58
    REMOVE_CHANNEL_METADATA = 59
    GET_ALL_CHANNEL_METADATA = 60

    SET_CHANNEL_MEMBERS = 61
    GET_CHANNEL_MEMBERS = 62
    REMOVE_CHANNEL_MEMBERS = 63
    MANAGE_CHANNEL_MEMBERS = 64

    SET_MEMBERSHIPS = 65
    GET_MEMBERSHIPS = 66
    REMOVE_MEMBERSHIPS = 67
    MANAGE_MEMBERSHIPS = 68

    # Handle unknown/future operation type
    UNEXPECTED_OPERATION_TYPE = -1

    @classmethod
    def _missing_(cls, value: Any) -> PubNubOperationType:
        if value is not None:
            _LOGGER.error("Unexpected operation type value: %s", value)
        return cls.UNEXPECTED_OPERATION_TYPE

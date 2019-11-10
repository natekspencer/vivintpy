"""Module that implements the VivintPubNubSubscribeListener class."""
import logging
from typing import Callable, Union

from pubnub.callbacks import SubscribeCallback
import pubnub.pubnub
import pubnub.pubnub_asyncio
import pubnub.models.consumer.common
import pubnub.models.consumer.pubsub


PN_SUBSCRIBE_KEY = 'sub-c-6fb03d68-6a78-11e2-ae8f-12313f022c90'
PN_CHANNEL = 'PlatformChannel'

_LOGGER = logging.getLogger(__name__)


class VivintPubNubSubscribeListener(SubscribeCallback):
    """PubNub Subscribe Listener."""
    def __init__(self, message_received_callback: Callable):
        super().__init__()
        self.__message_received_callback = message_received_callback

    def status(self, pubnub: Union[pubnub.pubnub.PubNub, pubnub.pubnub_asyncio.PubNubAsyncio],
               status: pubnub.models.consumer.common.PNStatus) -> None:
        """Handler called on status updates."""
        _LOGGER.info(f'pubnub status update {status.category}, error: {status.error}, error_data: {status.error_data}')

    def message(self, pubnub: Union[pubnub.pubnub.PubNub, pubnub.pubnub_asyncio.PubNubAsyncio],
                message: pubnub.models.consumer.pubsub.PNMessageResult) -> None:
        """Handler called on each message received."""
        self.__message_received_callback(message.message)

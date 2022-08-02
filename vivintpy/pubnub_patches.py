"""File for various patches to PubNub until fixed in module."""
from pubnub import pubnub_asyncio
from pubnub.endpoints.presence.heartbeat import Heartbeat
from pubnub.enums import PNHeartbeatNotificationOptions, PNStatusCategory
from pubnub.models.consumer.common import PNStatus
from pubnub.pubnub_asyncio import (
    AsyncioSubscriptionManager,
    PubNubAsyncioException,
    asyncio,
)

# pylint: disable=protected-access, fixme


async def patched_perform_heartbeat_loop(self: AsyncioSubscriptionManager) -> None:
    """
    Patched `_perform_heartbeat_loop` function on pubnub's `AsyncioSubscriptionManager` class.

    Correctly adheres to setting for heartbeat_notification_options.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    if self._heartbeat_call is not None:
        # TODO: cancel call
        pass

    cancellation_event = asyncio.Event()
    state_payload = self._subscription_state.state_payload()
    presence_channels = self._subscription_state.prepare_channel_list(False)
    presence_groups = self._subscription_state.prepare_channel_group_list(False)

    if len(presence_channels) == 0 and len(presence_groups) == 0:
        return

    try:
        heartbeat_call = (
            Heartbeat(self._pubnub)
            .channels(presence_channels)
            .channel_groups(presence_groups)
            .state(state_payload)
            .cancellation_event(cancellation_event)
            .future()
        )

        envelope = await heartbeat_call

        heartbeat_verbosity = self._pubnub.config.heartbeat_notification_options
        if heartbeat_verbosity == PNHeartbeatNotificationOptions.ALL or (
            envelope.status.is_error()
            and heartbeat_verbosity == PNHeartbeatNotificationOptions.FAILURES
        ):
            self._listener_manager.announce_status(envelope.status)

        if envelope.status is not None and envelope.status.category in [
            PNStatusCategory.PNTimeoutCategory,
            PNStatusCategory.PNNetworkIssuesCategory,
        ]:
            pass

    except PubNubAsyncioException:
        pass

    finally:
        cancellation_event.set()


pubnub_asyncio.AsyncioSubscriptionManager._perform_heartbeat_loop = (
    patched_perform_heartbeat_loop
)


def patched_is_error(self: PNStatus) -> bool:
    """
    Patched `is_error` function on pubnub's `PNStatus` class.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    return bool(self.error)


PNStatus.is_error = patched_is_error

"""File for various patches to PubNub until fixed in module."""
from pubnub import pubnub, pubnub_asyncio, utils
from pubnub.endpoints.presence.heartbeat import Heartbeat
from pubnub.endpoints.pubsub.subscribe import Subscribe
from pubnub.enums import (
    PNHeartbeatNotificationOptions,
    PNOperationType,
    PNReconnectionPolicy,
    PNStatusCategory,
)
from pubnub.errors import (
    PNERR_CLIENT_TIMEOUT,
    PNERR_CONNECTION_ERROR,
    PNERR_REQUEST_CANCELLED,
)
from pubnub.exceptions import PubNubException
from pubnub.models.consumer.common import PNStatus
from pubnub.pubnub_asyncio import PubNubAsyncioException, aiohttp, asyncio, logger


async def patched_request_future(self, options_func, cancellation_event):
    """
    Patched `request_future` function on pubnub's `PubNubAsyncio` class.

    Return status of PNStatusCategory.PNNetworkIssuesCategory when ClientConnectorError occurs.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    try:
        res = await self._request_helper(options_func, cancellation_event)
        return res
    except PubNubException as e:
        return PubNubAsyncioException(result=None, status=e.status)
    except asyncio.TimeoutError:
        return PubNubAsyncioException(
            result=None,
            status=options_func().create_status(
                PNStatusCategory.PNTimeoutCategory,
                None,
                None,
                exception=PubNubException(pn_error=PNERR_CLIENT_TIMEOUT),
            ),
        )
    except asyncio.CancelledError:
        return PubNubAsyncioException(
            result=None,
            status=options_func().create_status(
                PNStatusCategory.PNCancelledCategory,
                None,
                None,
                exception=PubNubException(pn_error=PNERR_REQUEST_CANCELLED),
            ),
        )
    except aiohttp.client_exceptions.ClientConnectorError:
        return PubNubAsyncioException(
            result=None,
            status=options_func().create_status(
                PNStatusCategory.PNNetworkIssuesCategory,
                None,
                None,
                exception=PubNubException(pn_error=PNERR_CONNECTION_ERROR),
            ),
        )
    except Exception as e:
        return PubNubAsyncioException(
            result=None,
            status=options_func().create_status(
                PNStatusCategory.PNUnknownCategory, None, None, e
            ),
        )


pubnub_asyncio.PubNubAsyncio.request_future = patched_request_future


async def patched_register_heartbeat_timer(self):
    """
    Patched `_register_heartbeat_timer` function on pubnub's `AsyncioReconnectionManager` class.

    Raise exception when there is an error on heartbeat call so that reconnect logic actually happens.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    while True:
        self._recalculate_interval()

        await asyncio.sleep(self._timer_interval)

        logger.debug("Reconnect loop at: %s" % utils.datetime_now())

        try:
            result = await self._pubnub.time().future()
            if result.status.is_error():
                raise result.status.error_data.exception
            self._connection_errors = 1
            self._callback.on_reconnect()
            break
        except Exception:
            if self._pubnub.config.reconnect_policy == PNReconnectionPolicy.EXPONENTIAL:
                logger.debug(
                    "Reconnect interval increment at: %s" % utils.datetime_now()
                )
                self._connection_errors += 1


pubnub_asyncio.AsyncioReconnectionManager._register_heartbeat_timer = (
    patched_register_heartbeat_timer
)


async def patched_start_subscribe_loop(self):
    """
    Patched `_start_subscribe_loop` function on pubnub's `AsyncioSubscriptionManager` class.

    Correctly call `_start_subscribe_loop` on timeouts.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    self._stop_subscribe_loop()

    await self._subscription_lock.acquire()

    combined_channels = self._subscription_state.prepare_channel_list(True)
    combined_groups = self._subscription_state.prepare_channel_group_list(True)

    if len(combined_channels) == 0 and len(combined_groups) == 0:
        self._subscription_lock.release()
        return

    self._subscribe_request_task = asyncio.ensure_future(
        Subscribe(self._pubnub)
        .channels(combined_channels)
        .channel_groups(combined_groups)
        .timetoken(self._timetoken)
        .region(self._region)
        .filter_expression(self._pubnub.config.filter_expression)
        .future()
    )

    e = await self._subscribe_request_task

    if self._subscribe_request_task.cancelled():
        self._subscription_lock.release()
        return

    if e.is_error():
        if (
            e.status is not None
            and e.status.category == PNStatusCategory.PNCancelledCategory
        ):
            self._subscription_lock.release()
            return

        if (
            e.status is not None
            and e.status.category == PNStatusCategory.PNTimeoutCategory
        ):
            asyncio.create_task(self._start_subscribe_loop())
            self._subscription_lock.release()
            return

        logger.error("Exception in subscribe loop: %s" % str(e))

        if (
            e.status is not None
            and e.status.category == PNStatusCategory.PNAccessDeniedCategory
        ):
            e.status.operation = PNOperationType.PNUnsubscribeOperation

        # TODO: raise error
        self._listener_manager.announce_status(e.status)

        self._reconnection_manager.start_polling()
        self._subscription_lock.release()
        self.disconnect()
        return
    else:
        self._handle_endpoint_call(e.result, e.status)
        self._subscription_lock.release()
        self._subscribe_loop_task = asyncio.ensure_future(self._start_subscribe_loop())

    self._subscription_lock.release()


pubnub_asyncio.AsyncioSubscriptionManager._start_subscribe_loop = (
    patched_start_subscribe_loop
)


async def patched_perform_heartbeat_loop(self):
    """
    Patched `_perform_heartbeat_loop` function on pubnub's `AsyncioSubscriptionManager` class.

    Correctly adheres to setting for heartbeat_notification_options.
    Call `_start_subscribe_loop` on timeouts and network issues.

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
            await self._start_subscribe_loop()

    except PubNubAsyncioException:
        pass

    finally:
        cancellation_event.set()


pubnub_asyncio.AsyncioSubscriptionManager._perform_heartbeat_loop = (
    patched_perform_heartbeat_loop
)


def patched_is_error(self):
    """
    Patched `is_error` function on pubnub's `PNStatus` class.

    See https://github.com/pubnub/python/pull/101 for when this can be removed.
    """
    return self.error not in [None, False]


PNStatus.is_error = patched_is_error


old_endpoint_name_for_operation = pubnub.TelemetryManager.endpoint_name_for_operation


@staticmethod
def patched_endpoint_name_for_operation(operation_type):
    """
    Patched `endpoint_name_for_operation` function on pubnub's `TelemetryManager` class.

    Avoids KeyError(6) when operation_type == PNOperationType.PNHeartbeatOperation.

    See https://github.com/pubnub/python/pull/100 for when this can be removed.
    """
    return (
        "hb"
        if operation_type == PNOperationType.PNHeartbeatOperation
        else old_endpoint_name_for_operation(operation_type)
    )


pubnub.TelemetryManager.endpoint_name_for_operation = (
    patched_endpoint_name_for_operation
)

"""Module that implements the Vivint class."""

from __future__ import annotations

import asyncio
import logging

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError
from pubnub.enums import PNHeartbeatNotificationOptions, PNReconnectionPolicy
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio

from .const import (
    AuthUserAttribute,
    PubNubMessageAttribute,
    SystemAttribute,
    UserAttribute,
)
from .exceptions import VivintSkyApiError
from .pubnub import PN_CHANNEL, PN_SUBSCRIBE_KEY, VivintPubNubSubscribeListener
from .system import System
from .utils import first_or_none, send_deprecation_warning
from .vivintskyapi import VivintSkyApi

_LOGGER = logging.getLogger(__name__)


class Account:
    """Class for interacting with VivintSky API using asyncio."""

    def __init__(
        self,
        username: str,
        password: str,
        persist_session: bool = False,
        client_session: aiohttp.ClientSession | None = None,
    ):
        """Initialize an account."""
        self.__connected = False
        self.__load_devices = False
        self.__pubnub: PubNubAsyncio | None = None
        self.__pubnub_listener: VivintPubNubSubscribeListener | None = None
        self._api = VivintSkyApi(
            username=username,
            password=password,
            persist_session=persist_session,
            client_session=client_session,
        )
        self.systems: list[System] = []

    @property
    def api(self) -> VivintSkyApi:
        """Return the API."""
        return self._api

    @property
    def vivintskyapi(self) -> VivintSkyApi:
        """Return the API."""
        send_deprecation_warning("vivintskyapi", "api")
        return self.api

    @property
    def connected(self) -> bool:
        """Return True if connected."""
        return self.__connected

    async def connect(
        self, load_devices: bool = False, subscribe_for_realtime_updates: bool = False
    ) -> None:
        """Connect to the VivintSky API."""
        _LOGGER.debug("Connecting to VivintSky")

        self.__load_devices = load_devices

        # initialize the vivintsky cloud session
        authuser_data = await self.api.connect()
        self.__connected = True

        # subscribe to pubnub for realtime updates
        if subscribe_for_realtime_updates:
            _LOGGER.debug("Subscribing to PubNub for realtime updates")
            await self.subscribe_for_realtime_updates(authuser_data)

        # load all systems, panels and devices
        if self.__load_devices:
            _LOGGER.debug("Loading devices")
            await self.refresh(authuser_data)

    async def disconnect(self) -> None:
        """Disconnect from the API."""
        _LOGGER.debug("Disconnecting from VivintSky")
        if self.connected:
            if self.__pubnub:
                self.__pubnub.remove_listener(self.__pubnub_listener)
                await self.__pubnub_unsubscribe_all()
                await self.__pubnub.stop()
        await self.api.disconnect()
        self.__connected = False

    async def __pubnub_unsubscribe_all(self) -> None:
        """
        Unsubscribe from all channels and wait for the response.

        The pubnub code doesn't properly wait for the unsubscribe event to finish or to
        be canceled, so we have to manually do it by finding the coroutine in asyncio.
        """
        assert self.__pubnub
        self.__pubnub.unsubscribe_all()
        tasks = [
            task
            for task in asyncio.all_tasks()
            if getattr(getattr(task.get_coro(), "cr_code", None), "co_name", None)
            == "_send_leave_helper"
        ]
        await asyncio.gather(*tasks)

    async def verify_mfa(self, code: str) -> None:
        """Verify multi-factor authentication with the VivintSky API."""
        await self.api.verify_mfa(code)

        # load all systems, panels and devices
        if self.__load_devices:
            _LOGGER.debug("Loading devices")
            await self.refresh()

    async def refresh(self, authuser_data: dict | None = None) -> None:
        """Refresh the account."""
        # make a call to vivint's authuser endpoint to get a list of all the system_accounts (locations) & panels if not supplied
        if not authuser_data:
            try:
                authuser_data = await self.api.get_authuser_data()
            except (ClientConnectionError, VivintSkyApiError):
                _LOGGER.error("Unable to refresh system(s)")

        if authuser_data:
            # for each system_account, make another call to load all the devices
            for system_data in authuser_data[AuthUserAttribute.USERS][
                UserAttribute.SYSTEM
            ]:
                # is this an existing account_system?
                system = first_or_none(
                    self.systems,
                    lambda system, system_data=system_data: system.id  # type: ignore
                    == system_data[SystemAttribute.PANEL_ID],
                )
                if system:
                    await system.refresh()
                else:
                    full_system_data = await self.api.get_system_data(
                        system_data[SystemAttribute.PANEL_ID]
                    )
                    self.systems.append(
                        System(
                            data=full_system_data,
                            api=self.api,
                            name=system_data.get(SystemAttribute.SYSTEM_NICKNAME),
                            is_admin=system_data.get(SystemAttribute.ADMIN, False),
                        )
                    )

            _LOGGER.debug(
                "Refreshed %s system(s)",
                len(authuser_data[AuthUserAttribute.USERS][UserAttribute.SYSTEM]),
            )

    async def subscribe_for_realtime_updates(
        self, authuser_data: dict | None = None
    ) -> None:
        """Subscribe to PubNub for realtime updates."""
        # make a call to vivint's authuser endpoint to get message broadcast channel if not supplied
        if not authuser_data:
            authuser_data = await self.api.get_authuser_data()

        user_data = authuser_data[AuthUserAttribute.USERS]

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = PN_SUBSCRIBE_KEY
        pnconfig.uuid = f"pn-{user_data[UserAttribute.ID].upper()}"
        pnconfig.ssl = True
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.heartbeat_notification_options = (
            PNHeartbeatNotificationOptions.FAILURES
        )

        self.__pubnub = PubNubAsyncio(pnconfig)
        self.__pubnub_listener = VivintPubNubSubscribeListener(
            self.handle_pubnub_message
        )
        self.__pubnub.add_listener(self.__pubnub_listener)

        pn_channel = (
            f"{PN_CHANNEL}#{user_data[UserAttribute.MESSAGE_BROADCAST_CHANNEL]}"
        )
        self.__pubnub.subscribe().channels(pn_channel).with_presence().execute()

    def handle_pubnub_message(self, message: dict) -> None:
        """Handle a pubnub message."""
        panel_id = message.get(PubNubMessageAttribute.PANEL_ID)
        if not panel_id:
            _LOGGER.debug(
                "PubNub message ignored (no panel id specified): %s",
                message,
            )
            return

        system = first_or_none(self.systems, lambda system: system.id == panel_id)
        if not system:
            _LOGGER.debug("No system found with id %s: %s", panel_id, message)
            return

        system.handle_pubnub_message(message)

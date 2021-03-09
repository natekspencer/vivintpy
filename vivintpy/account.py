"""Module that implements the Vivint class."""
import logging
from typing import List, Optional

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError

import pubnub
from pubnub.enums import PNHeartbeatNotificationOptions, PNReconnectionPolicy
from pubnub.pnconfiguration import PNConfiguration

from .const import (
    AuthUserAttribute,
    PubNubMessageAttribute,
    SystemAttribute,
    UserAttribute,
)
from .pubnub import (
    PN_CHANNEL,
    PN_SUBSCRIBE_KEY,
    VivintPubNubSubscribeListener,
    pubnub_asyncio,
)
from .system import System
from .utils import first_or_none
from .vivintskyapi import VivintSkyApi

_LOGGER = logging.getLogger(__name__)


class Account:
    """Class for interacting with VivintSky API using asyncio"""

    def __init__(
        self,
        username: str,
        password: str,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__connected = False
        self.__pubnub: pubnub_asyncio.PubNubAsyncio = None
        self.__pubnub_listener: VivintPubNubSubscribeListener = None
        self.vivintskyapi = VivintSkyApi(username, password, client_session)
        self.systems: List[System] = []

    @property
    def connected(self):
        """Return True if connected."""
        return self.__connected

    async def connect(
        self,
        load_devices: bool = False,
        subscribe_for_realtime_updates: bool = False,
    ) -> None:
        """Connects to vivintsky cloud service."""

        _LOGGER.debug("connecting to vivintsky")
        # initialize the vivintsky cloud session
        authuser_data = await self.vivintskyapi.connect()

        # load all systems, panels and devices
        if load_devices:
            _LOGGER.debug("loading devices")
            await self.refresh(authuser_data)

        # subscribe to pubnub for realtime updates
        if subscribe_for_realtime_updates:
            _LOGGER.debug("subscribing to pubnub for realtime updates")
            await self.subscribe_for_realtime_updates(authuser_data)

        self.__connected = True

    async def disconnect(self) -> None:
        _LOGGER.debug("disconnecting from vivintsky")
        if self.connected:
            if self.__pubnub:
                self.__pubnub.remove_listener(self.__pubnub_listener)
                self.__pubnub.unsubscribe_all()
                self.__pubnub.stop()
            await self.vivintskyapi.disconnect()
        self.__connected = False

    async def refresh(self, authuser_data: dict = None) -> None:
        # make a call to vivint's authuser endpoint to get a list of all the system_accounts (locations) & panels if not supplied
        if not authuser_data:
            try:
                authuser_data = await self.vivintskyapi.get_authuser_data()
            except ClientConnectionError:
                _LOGGER.error("Unable to refresh system(s).")

        if authuser_data:
            # for each system_account, make another call to load all the devices
            for system_data in authuser_data[AuthUserAttribute.USERS][
                UserAttribute.SYSTEM
            ]:
                # is this an existing account_system?
                system = first_or_none(
                    self.systems,
                    lambda system: system.id == system_data[SystemAttribute.PANEL_ID],
                )
                if system:
                    await system.refresh()
                else:
                    full_system_data = await self.vivintskyapi.get_system_data(
                        system_data[SystemAttribute.PANEL_ID]
                    )
                    self.systems.append(
                        System(
                            system_data.get(SystemAttribute.SYSTEM_NICKNAME),
                            full_system_data,
                            self.vivintskyapi,
                        )
                    )

            _LOGGER.debug(
                f"Refreshed {len(authuser_data[AuthUserAttribute.USERS][UserAttribute.SYSTEM])} system(s)."
            )

    async def subscribe_for_realtime_updates(self, authuser_data: dict = None) -> None:
        """Subscribes to PubNub for realtime updates."""
        # make a call to vivint's authuser endpoint to get message broadcast channel if not supplied
        if not authuser_data:
            authuser_data = await self.vivintskyapi.get_authuser_data()

        pubnub.set_stream_logger("pubnub", logging.INFO)

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = PN_SUBSCRIBE_KEY
        pnconfig.ssl = True
        pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
        pnconfig.heartbeat_notification_options = (
            PNHeartbeatNotificationOptions.FAILURES
        )

        self.__pubnub = pubnub_asyncio.PubNubAsyncio(pnconfig)
        self.__pubnub_listener = VivintPubNubSubscribeListener(
            self.handle_pubnub_message
        )
        self.__pubnub.add_listener(self.__pubnub_listener)

        pn_channel = f"{PN_CHANNEL}#{authuser_data[AuthUserAttribute.USERS][UserAttribute.MESSAGE_BROADCAST_CHANNEL]}"
        self.__pubnub.subscribe().channels(pn_channel).with_presence().execute()

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""
        panel_id = message.get(PubNubMessageAttribute.PANEL_ID)
        if not panel_id:
            _LOGGER.info("No panel id specified - ignoring pubnub message.")
            return

        system = first_or_none(self.systems, lambda system: system.id == panel_id)
        if not system:
            _LOGGER.info(f"No system found with id {panel_id}.")
            return

        system.handle_pubnub_message(message)

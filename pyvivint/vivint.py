"""Module that implements the Vivint class."""
import asyncio
import json
import logging
from typing import List, Optional

import aiohttp

import pubnub
import pyvivint.system
from pubnub.enums import PNHeartbeatNotificationOptions, PNReconnectionPolicy
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio
from pyvivint.constants import AuthUserAttribute
from pyvivint.constants import PubNubMessageAttribute as MessageAttributes
from pyvivint.pubnub import PN_CHANNEL, PN_SUBSCRIBE_KEY, VivintPubNubSubscribeListener
from pyvivint.system import System
from pyvivint.utils import add_async_job, first_or_none
from pyvivint.vivintskyapi import VivintSkyApi

_LOGGER = logging.getLogger(__name__)


class Vivint:
    """Class for interacting with VivintSky API using asyncio"""

    def __init__(
        self,
        username: str,
        password: str,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__pubnub: pubnub.pubnub_asyncio.PubNubAsyncio = None
        self.vivintskyapi = VivintSkyApi(username, password, client_session)
        self.systems: List[pyvivint.system.System] = []

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

    async def disconnect(self) -> None:
        _LOGGER.debug("disconnecting from vivintsky")
        await self.vivintskyapi.disconnect()

    async def refresh(self, authuser_data: dict = None) -> None:
        # make a call to vivint's authuser endpoint to get a list of all the system_accounts (locations) & panels if not supplied
        if not authuser_data:
            authuser_data = await self.vivintskyapi.get_authuser_data()

        # for each system_account, make another call to load all the devices
        for system_data in authuser_data["u"]["system"]:
            # is this an existing account_system?
            system = first_or_none(
                self.systems, lambda system: system.id == system_data["panid"]
            )
            if system:
                await system.refresh()
            else:
                full_system_data = await self.vivintskyapi.get_system_data(
                    system_data["panid"]
                )
                self.systems.append(
                    System(system_data.get("sn"), full_system_data, self.vivintskyapi)
                )

        _LOGGER.debug(f"loaded {len(self.systems)} system(s)")

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
        pnconfig.heartbeat_notification_options = PNHeartbeatNotificationOptions.ALL

        self.__pubnub = PubNubAsyncio(pnconfig)
        self.__pubnub.add_listener(
            VivintPubNubSubscribeListener(self.handle_pubnub_message)
        )

        pn_channel = f"{PN_CHANNEL}#{authuser_data[AuthUserAttribute.USERS][AuthUserAttribute.UserAttribute.MESSAGE_BROADCAST_CHANNEL]}"
        self.__pubnub.subscribe().channels(pn_channel).with_presence().execute()

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""
        _LOGGER.info(f"message: {json.dumps(message)}")

        panel_id = message.get(MessageAttributes.PANEL_ID)
        if not panel_id:
            _LOGGER.info("ignoring pubnub message. No panel_id specified")
            return

        system = first_or_none(self.systems, lambda system: system.id == panel_id)
        if not system:
            _LOGGER.info(f"no system found with id {panel_id}")
            return

        system.handle_pubnub_message(message)

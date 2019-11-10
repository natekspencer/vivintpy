"""Module that implements the Vivint class."""
import asyncio
import aiohttp
import json
import logging
import time

from typing import List, Optional

import pubnub
from pubnub.enums import PNReconnectionPolicy, PNHeartbeatNotificationOptions
from pubnub.pubnub_asyncio import PubNubAsyncio
from pubnub.pnconfiguration import PNConfiguration

import pyvivint.system
from pyvivint.enums import AuthUserAttributes, PubNumMessageAttributes as MessageAttributes
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
            loop: Optional[asyncio.events.AbstractEventLoop] = None,
            client_session: Optional[aiohttp.ClientSession] = None
    ):
        self.__loop: asyncio.events.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.__pubnub: pubnub.pubnub_asyncio.PubNubAsyncio = None
        self.vivintskyapi = VivintSkyApi(username, password, self.__loop, client_session)
        self.systems: List[pyvivint.system.System] = []

    async def connect(
        self,
        load_devices: bool = False,
        subscribe_for_realtime_updates: bool = False,
        enable_token_auto_refresh: bool = False
    ) -> None:
        """Connects to vivintsky cloud service."""

        _LOGGER.debug('connecting to vivintsky')
        # initialize the vivintsky cloud session
        await self.vivintskyapi.connect()

        # load all systems, panels and devices
        if load_devices:
            _LOGGER.debug('loading devices')
            await self.refresh()

        # set up loop to periodically refresh the token
        if enable_token_auto_refresh:
            _LOGGER.debug('setting up token auto refresh loop')
            self.setup_token_refresh_handler()

        # subscript to pubnub for realtime updates
        if subscribe_for_realtime_updates:
            _LOGGER.debug('subscribing to pubnub for realtime updates')
            await self.subscripbe_for_realtime_updates()

    async def disconnect(self) -> None:
        _LOGGER.debug('disconnecting from vivintsky')
        await self.vivintskyapi.disconnect()

    async def refresh(self) -> None:
        # make a call to vivint's userauth endpoint to get a list of all the system_accounts (locations) & panels
        authuser_data = await self.vivintskyapi.get_authuser_data()

        # for each system_account, make another call to load all the devices
        for system_data in authuser_data['u']['system']:
            # is this an existing account_system?
            system = first_or_none(self.systems, lambda system: system.id == system_data['panid'])
            if system:
                await system.refresh()
            else:
                full_system_data = await self.vivintskyapi.get_system_data(system_data['panid'])
                self.systems.append(System(full_system_data, self.vivintskyapi))

        _LOGGER.debug(f'loaded {len(self.systems)} system(s)')

    def setup_token_refresh_handler(self) -> None:
        """Set up the token refresh handler."""
        add_async_job(self.__token_refresh_handler)

    async def __token_refresh_handler(self) -> None:
        """Periodically refreshes the idtoken."""
        while True:
            id_token = self.vivintskyapi.parse_id_token(self.vivintskyapi.id_token)
            if id_token['payload']['exp'] - time.time() < 60:
                await self.vivintskyapi.refresh_token()

            await asyncio.sleep(1)

    async def subscripbe_for_realtime_updates(self) -> None:
        """Subscribes to PubNub for realtime updates."""
        # make a call to vivint's userauth endpoint
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

        pn_channel = f'{PN_CHANNEL}#{authuser_data[AuthUserAttributes.Users][AuthUserAttributes.UsersAttributes.MessageBroadcastChannel]}'  # noqa
        self.__pubnub.subscribe().channels(pn_channel).with_presence().execute()

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""
        _LOGGER.info(f"message: {json.dumps(message)}")

        panel_id = message.get(MessageAttributes.PanelId)
        if not panel_id:
            _LOGGER.info('ignoring pubnub message. No panel_id specified')
            return

        system = first_or_none(self.systems, lambda system: system.id == panel_id)
        if not system:
            _LOGGER.info(f'no system found with id {panel_id}')
            return

        system.handle_pubnub_message(message)

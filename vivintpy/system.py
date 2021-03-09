"""Module that implements the System class."""
import logging
from typing import List

from .const import PubNubMessageAttribute, SystemAttribute
from .devices.alarm_panel import AlarmPanel
from .entity import Entity
from .utils import first_or_none
from .vivintskyapi import VivintSkyApi

_LOGGER = logging.getLogger(__name__)


class System(Entity):
    """Describe a vivint system."""

    def __init__(self, name: str, data: dict, vivintskyapi: VivintSkyApi):
        super().__init__(data)
        self.__name = name
        self.vivintskyapi = vivintskyapi
        self.alarm_panels: List[AlarmPanel] = [
            AlarmPanel(panel_data, self)
            for panel_data in self.data[SystemAttribute.SYSTEM][
                SystemAttribute.PARTITION
            ]
        ]

    @property
    def id(self) -> str:
        """System's id"""
        return self.data[SystemAttribute.SYSTEM][SystemAttribute.PANEL_ID]

    @property
    def name(self) -> str:
        """System's name"""
        return self.__name

    async def refresh(self) -> None:
        """Reloads system's data from VivintSky API."""
        system_data = await self.vivintskyapi.get_system_data(self.id)

        for panel_data in system_data[SystemAttribute.SYSTEM][
            SystemAttribute.PARTITION
        ]:
            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel: panel.id == panel_data[SystemAttribute.PANEL_ID]
                and panel.partition_id == panel_data[SystemAttribute.PARTITION_ID],
            )
            if alarm_panel:
                alarm_panel.refresh(panel_data)
            else:
                self.alarm_panels.append(AlarmPanel(panel_data, self))

    def handle_pubnub_message(self, message: dict) -> None:
        """Handles a pubnub message."""

        if message[PubNubMessageAttribute.TYPE] == "account_system":
            # this is a system message
            operation = message.get(PubNubMessageAttribute.OPERATION)
            data = message.get(PubNubMessageAttribute.DATA)

            if data and operation == "u":
                self.update_data(data)

        elif message[PubNubMessageAttribute.TYPE] == "account_partition":
            # this is a message for one of the devices attached to this system
            partition_id = message.get(PubNubMessageAttribute.PARTITION_ID)
            if not partition_id:
                _LOGGER.debug(
                    f"ignoring account_partition message. No partition_id specified for system {self.id}"
                )
                return

            alarm_panel = first_or_none(
                self.alarm_panels,
                lambda panel: panel.id == self.id
                and panel.partition_id == partition_id,
            )

            if not alarm_panel:
                _LOGGER.debug(
                    f"no alarm panel found for system {self.id}, partition {partition_id}"
                )
                return

            alarm_panel.handle_pubnub_message(message)

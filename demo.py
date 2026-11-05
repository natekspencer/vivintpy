"""
Demo.

Run with your credentials in a .env file:

    uv run --env-file .env python demo.py

Put single quotes around a password that contains a $, or it won't load correctly.
"""

import asyncio
import logging
import os

import pubnub

from vivintpy.account import Account
from vivintpy.devices import VivintDevice
from vivintpy.devices.alarm_panel import AlarmPanel
from vivintpy.devices.camera import MOTION_DETECTED, Camera
from vivintpy.entity import UPDATE
from vivintpy.enums import ArmedState
from vivintpy.exceptions import VivintSkyApiMfaRequiredError

pubnub.set_stream_logger(name="pubnub", level=logging.ERROR)

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main."""
    logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Demo started")

    def camera_motion_callback(device: VivintDevice) -> None:
        _LOGGER.debug("Motion detected from camera: %s", device)

    def alarm_panel_update_callback(panel: AlarmPanel) -> None:
        # refreshes also emit updates, so only log actual changes
        status = (panel.state, panel.changed_by)
        if status != panel_statuses.get(panel):
            panel_statuses[panel] = status
            _LOGGER.debug(
                "Alarm panel %s: %s (changed by %s)",
                panel.id,
                panel.state.name,
                panel.changed_by,
            )

    def refresh_token_changed(_: str) -> None:
        # Each refresh token can only be used once, so a real application should save
        # this one now and use it to log in next time, instead of a password.
        _LOGGER.debug("Refresh token changed")

    panel_statuses: dict[AlarmPanel, tuple[ArmedState, str | None]] = {}

    account = Account(
        username=os.environ["username"],
        password=os.environ["password"],
        on_refresh_token_changed=refresh_token_changed,
    )
    try:
        await account.connect(load_devices=True, subscribe_for_realtime_updates=True)
    except VivintSkyApiMfaRequiredError:
        code = input("Enter MFA Code: ")
        await account.verify_mfa(code)
        _LOGGER.debug("MFA verified")
        # verify_mfa doesn't subscribe to pubnub, so do it here
        await account.subscribe_for_realtime_updates()

    _LOGGER.debug("Discovered systems & devices:")
    for system in account.systems:
        _LOGGER.debug(f"\tSystem {system.id}")
        for alarm_panel in system.alarm_panels:
            _LOGGER.debug(
                f"\t\tAlarm panel {alarm_panel.id}:{alarm_panel.partition_id} ({alarm_panel.software_version})"
            )
            panel_statuses[alarm_panel] = (alarm_panel.state, alarm_panel.changed_by)
            alarm_panel.on(
                UPDATE,
                lambda _, panel=alarm_panel: alarm_panel_update_callback(panel),
            )
            for device in alarm_panel.devices:
                _LOGGER.debug(f"\t\t\tDevice: {device} ({device.software_version})")
                if isinstance(device, Camera):
                    device.on(
                        MOTION_DETECTED,
                        lambda event: camera_motion_callback(event["device"]),
                    )

    try:
        while True:
            await asyncio.sleep(300)
            await account.refresh()
    except Exception as e:  # noqa: BLE001
        _LOGGER.debug(e)
    finally:
        await account.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

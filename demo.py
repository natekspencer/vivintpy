import asyncio
import logging
import os

import pubnub

from vivintpy.account import Account
from vivintpy.devices import VivintDevice
from vivintpy.devices.camera import MOTION_DETECTED, Camera
from vivintpy.exceptions import VivintSkyApiMfaRequiredError

pubnub.set_stream_logger(name="pubnub", level=logging.ERROR)


async def main():
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Demo started")

    def camera_motion_callback(device: VivintDevice) -> None:
        logging.debug("Motion detected from camera: %s", device)

    account = Account(username=os.environ["username"], password=os.environ["password"])
    try:
        await account.connect(load_devices=True, subscribe_for_realtime_updates=True)
    except VivintSkyApiMfaRequiredError:
        code = input("Enter MFA Code: ")
        await account.verify_mfa(code)
        logging.debug("MFA verified")

    logging.debug("Discovered systems & devices:")
    for system in account.systems:
        logging.debug(f"\tSystem {system.id}")
        for alarm_panel in system.alarm_panels:
            logging.debug(
                f"\t\tAlarm panel {alarm_panel.id}:{alarm_panel.partition_id}"
            )
            for device in alarm_panel.devices:
                logging.debug(f"\t\t\tDevice: {device}")
                if isinstance(device, Camera):
                    device.on(
                        MOTION_DETECTED,
                        lambda event: camera_motion_callback(event["device"]),
                    )

    try:
        while True:
            await asyncio.sleep(300)
            await account.refresh()
    except Exception as e:
        logging.debug(e)
    finally:
        await account.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import os

import pubnub

from vivintpy.account import Account
from vivintpy.devices.camera import MOTION_DETECTED, Camera

pubnub.set_stream_logger(name="pubnub", level=logging.ERROR)


async def main():
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Demo started")

    def camera_motion_callback(**kwargs):
        logging.debug("Motion detected from camera: %s", kwargs)

    account = Account(username=os.environ["username"], password=os.environ["password"])

    await account.connect(load_devices=True, subscribe_for_realtime_updates=True)

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
                        MOTION_DETECTED, lambda event: camera_motion_callback(**event)
                    )

    try:
        while True:
            await asyncio.sleep(300)
            await account.refresh()
    finally:
        await account.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

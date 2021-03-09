import asyncio
import logging
import os

from vivintpy.account import Account


async def main():
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("demo started")

    account = Account(username=os.environ["username"], password=os.environ["password"])

    await account.connect(load_devices=True, subscribe_for_realtime_updates=True)

    logging.info("discovered systems & devices:")
    for system in account.systems:
        logging.info(f"\tsystem {system.id}")
        for alarm_panel in system.alarm_panels:
            logging.info(f"\t\talarm panel {alarm_panel.id}:{alarm_panel.partition_id}")

            for device in alarm_panel.devices:
                logging.info(f"\t\t\tdevice: {device}")

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await account.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

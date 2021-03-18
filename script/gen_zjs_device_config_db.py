#!/usr/bin/env python3
"""Generate an updated zjs_device_config_db.json."""
import asyncio
import logging
import sys

from vivintpy.zjs_device_config_db import (
    _device_config_db_file_exists,
    download_zjs_device_config_db,
)

logging.getLogger("vivintpy.zjs_device_config_db").setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)


async def main():
    """Run the script."""
    logging.debug("Running script")

    await download_zjs_device_config_db()

    if not _device_config_db_file_exists():
        logging.error("Unable to generate zjs_device_config_db.json")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

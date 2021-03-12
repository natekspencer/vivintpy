import asyncio
import concurrent.futures
import json
import logging
import os
import re
import shutil
import tarfile
import threading
from pathlib import Path

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

TMP_DIR = os.path.join(os.path.dirname(__file__), "./.tmp/")
ZJS_TAR_FILE = os.path.join(TMP_DIR, "zjs.tar.gz")
ZJS_TAR_URL = "http://github.com/zwave-js/node-zwave-js/archive/master.tar.gz"
ZJS_TAR_CONFIG_BASE = "node-zwave-js-master/packages/config/config/"
ZJS_DEVICE_CONFIG_DB_FILE = os.path.join(
    os.path.dirname(__file__), "zjs_device_config_db.json"
)

__MUTEX = threading.Lock()


def get_zwave_device_info(
    manufacturer_id: int, product_type: int, product_id: int
) -> dict:
    """Lookup the Z-Wave device based on the manufacturer id, product type, and product id"""
    key = f"0x{manufacturer_id:04x}:0x{product_type:04x}:0x{product_id:04x}"
    return get_zjs_device_config_db().get(key, {})


def get_zjs_device_config_db() -> dict:
    """Returns the Z-Wave JS device config db as a dict."""
    if not _device_config_db_file_exists():
        pool = concurrent.futures.ThreadPoolExecutor()
        result = pool.submit(asyncio.run, download_zjs_device_config_db()).result()
        return result

    return _load_db_from_file()


def _device_config_db_file_exists() -> bool:
    """Returns True if the device config db file exists."""
    return (
        os.path.isfile(ZJS_DEVICE_CONFIG_DB_FILE)
        and os.path.getsize(ZJS_DEVICE_CONFIG_DB_FILE) > 0
    )


def _load_db_from_file() -> dict:
    """Loads the Z-Wave JS device config from the saved JSON file."""
    data = {}
    if _device_config_db_file_exists():
        with open(ZJS_DEVICE_CONFIG_DB_FILE) as f:
            data = json.load(f)
    return data


async def download_zjs_device_config_db():
    """Downloads the Z-Wave JS device config database."""
    with __MUTEX:
        if not _device_config_db_file_exists():
            _LOGGER.info("Beginning download process")
            _clean_temp_directory(create=True)
            await _download_zjs_tarfile()
            _extract_zjs_config_files()
            data = _create_db_from_zjs_config_files()
            _clean_temp_directory()
            return data
        else:
            return _load_db_from_file()


def _clean_temp_directory(create: bool = False) -> None:
    """Ensures the temp directory is empty and creates it if specified."""
    if os.path.exists(TMP_DIR):
        _LOGGER.info("Removing temp directory")
        shutil.rmtree(TMP_DIR)

    if create:
        _LOGGER.info("Creating temp directory")
        os.mkdir(TMP_DIR)


async def _download_zjs_tarfile() -> None:
    """Downloads the Z-Wave JS tarfile from http://github.com/zwave-js/node-zwave-js."""
    _LOGGER.info("Downloading tarfile from Z-Wave JS")
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(ZJS_TAR_URL) as response:
                with open(ZJS_TAR_FILE, "wb") as file:
                    async for data in response.content.iter_chunked(1024):
                        file.write(data)


def _extract_zjs_config_files() -> None:
    """Extracts the Z-Wave JSON config files."""
    manufacturers_path = "".join([ZJS_TAR_CONFIG_BASE, "manufacturers.json"])
    devices_path = "".join([ZJS_TAR_CONFIG_BASE, "devices/"])

    def members(tf):
        l = len(ZJS_TAR_CONFIG_BASE)
        for member in tf.getmembers():
            if member.path.startswith(manufacturers_path) or (
                member.path.startswith(devices_path)
                and member.path.endswith(".json")
                and "/templates/" not in member.path
            ):
                member.path = member.path[l:]
                yield member

    _LOGGER.info("Extracting config files from download")
    with tarfile.open(ZJS_TAR_FILE) as tar:
        tar.extractall(members=members(tar), path=TMP_DIR)


def _create_db_from_zjs_config_files() -> dict:
    """Parses the Z-Wave JSON config files and creates a consolidated device db."""
    _LOGGER.info("Parsing extracted config files")
    json_files = Path(os.path.join(TMP_DIR, "devices")).glob("**/*.json")

    device_db = {}

    for file in json_files:
        data = {}
        try:
            with open(file) as json_file:
                json_string = "".join(
                    re.sub("(([^:]|^)//[^a-zA-Z\d:].*)|(/\*.*\*/)", "", line)
                    for line in json_file.readlines()
                )
                data = json.loads(json_string)
        except:
            print("oops, couldn't parse file %s", file)

        manufacturer_id = data.get("manufacturerId")
        manufacturer = data.get("manufacturer")
        label = data.get("label")
        description = data.get("description")

        for device in data.get("devices", []):
            product_type = device.get("productType")
            product_id = device.get("productId")
            device_db[f"{manufacturer_id}:{product_type}:{product_id}"] = {
                "manufacturer": manufacturer,
                "label": label,
                "description": description,
            }

    _LOGGER.info("Creating consolidated device db")
    with open(ZJS_DEVICE_CONFIG_DB_FILE, "w") as device_file:
        device_file.write(json.dumps(device_db))

    return device_db

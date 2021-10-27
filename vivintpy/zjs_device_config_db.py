"""Script to generate Z-Wave device data."""
import json
import logging
import os
import re
import shutil
import tarfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)
UPDATED_AT = "updated_at"

TMP_DIR = os.path.join(os.path.dirname(__file__), "./.tmp/")
REPO_URL = "https://api.github.com/repos/zwave-js/node-zwave-js"
ZJS_TAR_FILE = os.path.join(TMP_DIR, "zjs.tar.gz")
ZJS_TAR_CONFIG_BASE = "/packages/config/config/"
ZJS_DEVICE_CONFIG_DB_FILE = os.path.join(
    os.path.dirname(__file__), "zjs_device_config_db.json"
)

__MUTEX = threading.Lock()


def get_zwave_device_info(
    manufacturer_id: int, product_type: int, product_id: int
) -> dict:
    """Lookup the Z-Wave device based on the manufacturer id, product type and product id."""
    key = f"0x{manufacturer_id:04x}:0x{product_type:04x}:0x{product_id:04x}"
    return _load_db_from_file().get(key, {})


def _device_config_db_file_exists() -> bool:
    """Return True if the device config db file exists."""
    return (
        os.path.isfile(ZJS_DEVICE_CONFIG_DB_FILE)
        and os.path.getsize(ZJS_DEVICE_CONFIG_DB_FILE) > 0
    )


def _load_db_from_file() -> dict:
    """Load the Z-Wave JS device config from the saved JSON file."""
    data = {}
    if _device_config_db_file_exists():
        with open(ZJS_DEVICE_CONFIG_DB_FILE) as f:
            data = json.load(f)
    return data


async def download_zjs_device_config_db() -> dict:
    """Download the Z-Wave JS device config database."""
    with __MUTEX:
        if await _is_new_version_available():
            start_date = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            _LOGGER.debug("Beginning download process")
            _clean_temp_directory(create=True)
            await _download_zjs_tarfile()
            _extract_zjs_config_files()
            data = _create_db_from_zjs_config_files(updated_at=start_date)
            _clean_temp_directory()
            return data
        else:
            _LOGGER.debug("An updated file was not created")
            return _load_db_from_file()


async def _is_new_version_available() -> bool:
    """Return `True` if a newer archive of the repo at http://github.com/zwave-js/node-zwave-js is available."""
    file_updated_at = _load_db_from_file().get(UPDATED_AT)
    if file_updated_at is None:
        _LOGGER.debug("File has not yet been created")
        return True
    file_updated_at = datetime.fromisoformat(file_updated_at)

    _LOGGER.debug("Retrieving last updated date from %s", REPO_URL)
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.get(REPO_URL) as response:
                if response.status != 200:
                    _LOGGER.debug("Unable to check last updated date from %s", REPO_URL)
                    return False
                updated_at = datetime.fromisoformat(
                    (await response.json()).get(UPDATED_AT).replace("Z", "")
                )
                _LOGGER.debug(
                    "Repo was last updated at %s, while saved file was last updated at %s",
                    updated_at,
                    file_updated_at,
                )
                return file_updated_at < updated_at


def _clean_temp_directory(create: bool = False) -> None:
    """Ensure the temp directory is empty and create it if specified."""
    if os.path.exists(TMP_DIR):
        _LOGGER.debug("Removing temp directory")
        shutil.rmtree(TMP_DIR)

    if create:
        _LOGGER.debug("Creating temp directory")
        os.mkdir(TMP_DIR)


async def _download_zjs_tarfile() -> None:
    """Download the Z-Wave JS tarfile from http://github.com/zwave-js/node-zwave-js."""
    download_url = f"{REPO_URL}/tarball"
    _LOGGER.debug("Downloading tarfile from %s", download_url)
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(download_url) as response:
                with open(ZJS_TAR_FILE, "wb") as file:
                    async for data in response.content.iter_chunked(1024):
                        file.write(data)


def _extract_zjs_config_files() -> None:
    """Extract the Z-Wave JSON config files."""

    def members(tf: tarfile.TarFile) -> Generator[tarfile.TarInfo, Any, Any]:
        base_path = f"{tf.firstmember.path}{ZJS_TAR_CONFIG_BASE}"
        manufacturers_path = f"{base_path}manufacturers.json"
        devices_path = f"{base_path}devices/"
        base_length = len(base_path)
        for member in tf.getmembers():
            if member.path.startswith(manufacturers_path) or (
                member.path.startswith(devices_path)
                and member.path.endswith(".json")
                and "/templates/" not in member.path
            ):
                member.path = member.path[base_length:]
                yield member

    _LOGGER.debug("Extracting config files from download")
    with tarfile.open(ZJS_TAR_FILE) as tar:
        tar.extractall(members=members(tar), path=TMP_DIR)


def _create_db_from_zjs_config_files(updated_at: str) -> dict:
    """Parse the Z-Wave JSON config files and create a consolidated device db."""
    _LOGGER.debug("Parsing extracted config files")
    json_files = Path(os.path.join(TMP_DIR, "devices")).glob("**/*.json")

    device_db = {}

    for file in json_files:
        data = {}
        try:
            with open(file) as json_file:
                json_string = "".join(
                    re.sub("((^|\\s+)//.*)|(/\\*.*\\*/)", "", line)
                    for line in json_file.readlines()
                )
                data = json.loads(json_string)
        except:  # noqa: E722
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

    if device_db == {}:
        _LOGGER.error("Unable to create consolidated device db")
    else:
        _LOGGER.debug("Creating consolidated device db")
        device_db.update({UPDATED_AT: updated_at})
        with open(ZJS_DEVICE_CONFIG_DB_FILE, "w") as device_file:
            device_file.write(json.dumps(device_db, sort_keys=True, indent=2))

    return device_db

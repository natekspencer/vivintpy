#!/usr/bin/env python3
"""Generate an updated zjs_device_config_db.json."""
import asyncio
import json
import logging
import os
import re
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

import aiohttp
import async_timeout

logging.getLogger("vivintpy.zjs_device_config_db").setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)

UPDATED_AT = "updated_at"
TMP_DIR = os.path.join(os.path.dirname(__file__), "./.tmp/")
REPO_URL = "https://api.github.com/repos/zwave-js/node-zwave-js"
ZJS_TAR_FILE = os.path.join(TMP_DIR, "zjs.tar.gz")
ZJS_TAR_CONFIG_BASE = "/packages/config/config/"
ZJS_DEVICE_CONFIG_DB_FILE = os.path.join(
    os.path.dirname(__file__), "../vivintpy/zjs_device_config_db.json"
)


def _clean_temp_directory(create: bool = False) -> None:
    """Ensure the temp directory is empty and create it if specified."""
    if os.path.exists(TMP_DIR):
        logging.debug("Removing temp directory")
        shutil.rmtree(TMP_DIR)

    if create:
        logging.debug("Creating temp directory")
        os.mkdir(TMP_DIR)


def _create_db_from_zjs_config_files(
    updated_at: str,
) -> dict[str, str | dict[str, str]]:
    """Parse the Z-Wave JSON config files and create a consolidated device db."""
    logging.debug("Parsing extracted config files")
    json_files = Path(os.path.join(TMP_DIR, "devices")).glob("**/*.json")

    device_db: dict[str, str | dict[str, str]] = {}

    for file in json_files:
        data = {}
        try:
            with open(file, encoding="utf-8") as json_file:
                json_string = "".join(
                    re.sub("((^|\\s+)//.*)|(/\\*.*\\*/)", "", line)
                    for line in json_file.readlines()
                )
                json_string = re.sub(r"(?m)^\s*?/\*(.|\n)*?\*/\s*?$", "", json_string)
                data = json.loads(json_string)
        except:  # noqa: E722 #pylint: disable=bare-except
            logging.error("Unable to parse file %s", file)
            continue

        manufacturer_id = data["manufacturerId"]
        manufacturer = data["manufacturer"]
        label = data["label"]
        description = data["description"]

        for device in data.get("devices", []):
            product_type = device.get("productType")
            product_id = device.get("productId")
            device_db[f"{manufacturer_id}:{product_type}:{product_id}"] = {
                "manufacturer": manufacturer,
                "label": label,
                "description": description,
            }

    if not device_db:
        logging.error("Unable to create consolidated device db")
    else:
        logging.debug("Creating consolidated device db")
        device_db.update({UPDATED_AT: updated_at})
        with open(ZJS_DEVICE_CONFIG_DB_FILE, "w", encoding="utf-8") as device_file:
            device_file.write(json.dumps(device_db, sort_keys=True, indent=2))

    return device_db


def _device_config_db_file_exists() -> bool:
    """Return True if the device config db file exists."""
    return (
        os.path.isfile(ZJS_DEVICE_CONFIG_DB_FILE)
        and os.path.getsize(ZJS_DEVICE_CONFIG_DB_FILE) > 0
    )


def _extract_zjs_config_files() -> None:
    """Extract the Z-Wave JSON config files."""

    def _members(tar_file: tarfile.TarFile) -> Generator[tarfile.TarInfo, Any, Any]:
        assert (firstmember := tar_file.next())
        base_path = f"{firstmember.path}{ZJS_TAR_CONFIG_BASE}"
        manufacturers_path = f"{base_path}manufacturers.json"
        devices_path = f"{base_path}devices/"
        base_length = len(base_path)
        for member in tar_file.getmembers():
            if member.path.startswith(manufacturers_path) or (
                member.path.startswith(devices_path)
                and member.path.endswith(".json")
                and "/templates/" not in member.path
            ):
                member.path = member.path[base_length:]
                yield member

    logging.debug("Extracting config files from download")
    with tarfile.open(ZJS_TAR_FILE) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, members=_members(tar), path=TMP_DIR)


def _load_db_from_file() -> dict[str, str | dict[str, str]]:
    """Load the Z-Wave JS device config from the saved JSON file."""
    data: dict[str, str | dict[str, str]] = {}
    if _device_config_db_file_exists():
        with open(ZJS_DEVICE_CONFIG_DB_FILE, encoding="utf-8") as device_file:
            data = json.load(device_file)
    return data


async def download_zjs_device_config_db() -> dict:
    """Download the Z-Wave JS device config database."""
    if await _is_new_version_available():
        start_date = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        logging.debug("Beginning download process")
        _clean_temp_directory(create=True)
        await _download_zjs_tarfile()
        _extract_zjs_config_files()
        data = _create_db_from_zjs_config_files(updated_at=start_date)
        _clean_temp_directory()
        return data
    logging.debug("Skipping file update")
    return _load_db_from_file()


async def _download_zjs_tarfile() -> None:
    """Download the Z-Wave JS tarfile from http://github.com/zwave-js/node-zwave-js."""
    download_url = f"{REPO_URL}/tarball"
    logging.debug("Downloading tarfile from %s", download_url)
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(download_url) as response:
                with open(ZJS_TAR_FILE, "wb") as file:
                    async for data in response.content.iter_chunked(1024):
                        file.write(data)


async def _is_new_version_available() -> bool:
    """Return `True` if a newer archive of the repo at http://github.com/zwave-js/node-zwave-js is available."""
    file_updated_at_str = _load_db_from_file().get(UPDATED_AT)
    if not isinstance(file_updated_at_str, str):
        logging.debug("File has not yet been created")
        return True
    file_updated_at = datetime.fromisoformat(file_updated_at_str)

    logging.debug("Retrieving last updated date from %s", REPO_URL)
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.get(REPO_URL) as response:
                if response.status != 200:
                    logging.debug("Unable to check last updated date from %s", REPO_URL)
                    return False
                updated_at = datetime.fromisoformat(
                    (await response.json()).get(UPDATED_AT).replace("Z", "")
                )
                logging.debug(
                    "Repo was last updated at %s, while saved file was last updated at %s",
                    updated_at,
                    file_updated_at,
                )
                return file_updated_at < updated_at


async def main() -> int:
    """Run the script."""
    logging.debug("Running script")

    await download_zjs_device_config_db()

    if not _device_config_db_file_exists():
        logging.error("Unable to generate zjs_device_config_db.json")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

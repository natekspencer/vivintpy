"""Script to generate Z-Wave device data."""

from __future__ import annotations

import json
import os

ZJS_DEVICE_CONFIG_DB_FILE = os.path.join(
    os.path.dirname(__file__), "zjs_device_config_db.json"
)
ZJS_DEVICE_DB: dict[str, str | dict[str, str]] = {}


def get_zwave_device_info(
    manufacturer_id: int | None, product_type: int | None, product_id: int | None
) -> dict[str, str]:
    """Lookup the Z-Wave device based on the manufacturer id, product type and product id."""
    key = f"0x{manufacturer_id:04x}:0x{product_type:04x}:0x{product_id:04x}"
    if isinstance((device_info := _get_zjs_db().get(key)), dict):
        return device_info
    return {}


def _get_zjs_db() -> dict[str, str | dict[str, str]]:
    """Load the Z-Wave JS device config from the saved JSON file."""
    global ZJS_DEVICE_DB  # pylint: disable=global-statement
    if not ZJS_DEVICE_DB:
        with open(ZJS_DEVICE_CONFIG_DB_FILE, encoding="utf-8") as device_file:
            ZJS_DEVICE_DB = json.load(device_file)
    return ZJS_DEVICE_DB

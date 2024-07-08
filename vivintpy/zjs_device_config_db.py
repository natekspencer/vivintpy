"""Script to generate Z-Wave device data."""

from __future__ import annotations

import json
import os
from typing import Final

with open(
    os.path.join(os.path.dirname(__file__), "zjs_device_config_db.json"),
    encoding="utf8",
) as file:
    ZJS_DEVICE_DB: Final[dict[str, str | dict[str, str]]] = json.load(file)


def get_zwave_device_info(
    manufacturer_id: int | None, product_type: int | None, product_id: int | None
) -> dict[str, str]:
    """Lookup the Z-Wave device based on the manufacturer id, product type and product id."""
    key = f"0x{manufacturer_id:04x}:0x{product_type:04x}:0x{product_id:04x}"
    if isinstance((device_info := ZJS_DEVICE_DB.get(key)), dict):
        return device_info
    return {}

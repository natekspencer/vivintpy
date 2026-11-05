"""Test the system."""

import logging
from unittest.mock import MagicMock

import pytest

from vivintpy.system import System

SYSTEM_ID = 1
ADAPTIVE_HOME_SETTINGS = {
    "t": "adaptive_home_settings",
    "op": "u",
    "da": {"home_state": 2, "system_id": SYSTEM_ID},
    "panid": SYSTEM_ID,
}


@pytest.fixture
def system() -> System:
    """Return a system without any alarm panels."""
    return System(
        {"system": {"panid": SYSTEM_ID, "u": [], "par": []}},
        MagicMock(),
        name="Home",
        is_admin=True,
    )


def test_adaptive_home_settings_message_is_not_a_warning(
    system: System, caplog: pytest.LogCaptureFixture
) -> None:
    """Test adaptive home settings aren't reported as an unknown message."""
    with caplog.at_level(logging.DEBUG, logger="vivintpy.system"):
        system.handle_pubnub_message(ADAPTIVE_HOME_SETTINGS)

    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert "Ignoring adaptive home settings" in caplog.text


def test_unknown_message_is_a_warning(
    system: System, caplog: pytest.LogCaptureFixture
) -> None:
    """Test a message type that isn't handled is still reported."""
    system.handle_pubnub_message({"t": "something_new"})

    assert "Unknown message received" in caplog.text

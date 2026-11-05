"""Test the alarm panel."""

from unittest.mock import MagicMock

import pytest

from vivintpy.entity import UPDATE
from vivintpy.enums import ArmedState
from vivintpy.system import System

SYSTEM_ID = 1


def create_system(*states: ArmedState) -> System:
    """Return a system with a panel in each of the states."""
    return System(
        {
            "system": {
                "panid": SYSTEM_ID,
                "u": [],
                "par": [
                    {"panid": SYSTEM_ID, "parid": index, "s": state.value, "d": []}
                    for index, state in enumerate(states, start=1)
                ],
            }
        },
        MagicMock(),
        name="Home",
        is_admin=True,
    )


def security_message(key: str, state: ArmedState, name: str | None) -> dict:
    """Return a message reporting what armed or disarmed the system."""
    return {
        "t": "account_system",
        "op": "u",
        "panid": SYSTEM_ID,
        "da": {key: {"n": name, "s": state.value, "ts": "2026-11-05T17:06:00"}},
    }


@pytest.mark.parametrize(
    ("key", "state"),
    [("seca", ArmedState.ARMED_STAY), ("secd", ArmedState.DISARMED)],
)
def test_changed_by(key: str, state: ArmedState) -> None:
    """Test the panel reports what armed or disarmed it and notifies listeners."""
    system = create_system(state)
    (panel,) = system.alarm_panels
    listener = MagicMock()
    panel.on(UPDATE, listener)

    system.handle_pubnub_message(security_message(key, state, "panel"))

    assert panel.changed_by == "panel"
    listener.assert_called_once()


def test_changed_by_only_updates_panels_in_the_state() -> None:
    """Test a partition in another state keeps what last changed it."""
    system = create_system(ArmedState.ARMED_AWAY, ArmedState.DISARMED)
    armed, disarmed = system.alarm_panels
    disarmed.update_changed_by("Earlier")

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "Person")
    )

    assert armed.changed_by == "Person"
    assert disarmed.changed_by == "Earlier"


def test_changed_by_before_the_state_update() -> None:
    """Test an event that arrives before the panel's own state update is kept."""
    system = create_system(ArmedState.DISARMED)
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_STAY, "Person")
    )
    system.handle_pubnub_message(
        {
            "t": "account_partition",
            "op": "u",
            "panid": SYSTEM_ID,
            "parid": panel.partition_id,
            "da": {"s": ArmedState.ARMED_STAY.value},
        }
    )

    assert panel.state == ArmedState.ARMED_STAY
    assert panel.changed_by == "Person"


def test_security_value_that_is_not_an_event_is_ignored() -> None:
    """Test a malformed value is skipped and doesn't stop a valid event."""
    system = create_system(ArmedState.DISARMED)
    (panel,) = system.alarm_panels
    message = security_message("secd", ArmedState.DISARMED, "Person")
    message["da"]["seca"] = True

    system.handle_pubnub_message(message)

    assert panel.changed_by == "Person"


def test_other_system_messages_keep_changed_by() -> None:
    """Test a system update without an event doesn't clear the value."""
    system = create_system(ArmedState.DISARMED)
    (panel,) = system.alarm_panels
    panel.update_changed_by("Person")

    system.handle_pubnub_message(
        {"t": "account_system", "op": "u", "panid": SYSTEM_ID, "da": {"s": 0}}
    )

    assert panel.changed_by == "Person"

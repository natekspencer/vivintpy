"""Test the alarm panel."""

import asyncio
from collections.abc import Iterator
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError

from vivintpy.account import Account
from vivintpy.api import VivintSkyApi
from vivintpy.entity import UPDATE
from vivintpy.enums import ArmedState
from vivintpy.exceptions import VivintSkyApiError
from vivintpy.system import System

SYSTEM_ID = 1
FOB = "Front Keyfob"
MESSAGE = "Your home was armed from the Front Keyfob"
TIMESTAMP = "2026-11-05T17:06:00"


def create_system(*states: ArmedState) -> System:
    """Return a system with a panel in each of the states."""
    api = MagicMock()
    api.get_history = AsyncMock(return_value=[])
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
        api,
        name="Home",
        is_admin=True,
    )


def security_message(
    key: str,
    state: ArmedState,
    name: str | None,
    timestamp: str = TIMESTAMP,
    **fields: str,
) -> dict:
    """Return a message reporting what armed or disarmed the system."""
    return {
        "t": "account_system",
        "op": "u",
        "panid": SYSTEM_ID,
        "da": {key: {"n": name, "s": state.value, "ts": timestamp, **fields}},
    }


def history_event(
    icon: str = "armed_away",
    device_name: str | None = FOB,
    timestamp: str = f"{TIMESTAMP}.000000",
) -> dict:
    """Return a history event."""
    return {
        "icon": icon,
        "me": MESSAGE,
        "ts": timestamp,
        "pnlctx": {"dn": device_name},
    }


@pytest.fixture(autouse=True)
def no_retry_delays() -> Iterator[None]:
    """Skip the delays between history lookups."""
    with patch("vivintpy.system.HISTORY_RETRY_DELAYS", (0, 0)):
        yield


async def finish_lookup(system: System) -> None:
    """Wait for any history lookup to finish."""
    tasks = asyncio.all_tasks() - {asyncio.current_task()}
    results = await asyncio.gather(*tasks, return_exceptions=True)
    system.cancel_changed_by_lookup()
    for result in results:
        if isinstance(result, Exception):
            raise result


def history_mock(system: System) -> AsyncMock:
    """Return the mock for a system's history."""
    return cast(AsyncMock, system.api.get_history)


def create_fob_system(state: ArmedState, *results: object) -> System:
    """Return a system whose history gives each of the results in turn."""
    system = create_system(state)
    history_mock(system).side_effect = results
    return system


@pytest.mark.parametrize(
    ("key", "state"),
    [("seca", ArmedState.ARMED_STAY), ("secd", ArmedState.DISARMED)],
)
async def test_changed_by(key: str, state: ArmedState) -> None:
    """Test the panel reports what armed or disarmed it and notifies listeners."""
    system = create_fob_system(state, [], [])
    (panel,) = system.alarm_panels
    listener = MagicMock()
    panel.on(UPDATE, listener)

    system.handle_pubnub_message(security_message(key, state, "panel"))

    assert panel.changed_by == "panel"
    listener.assert_called_once()
    await finish_lookup(system)


async def test_changed_by_only_updates_panels_in_the_state() -> None:
    """Test a partition in another state keeps what last changed it."""
    system = create_system(ArmedState.ARMED_AWAY, ArmedState.DISARMED)
    armed, disarmed = system.alarm_panels
    disarmed.update_changed_by("Earlier")

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "Person")
    )

    assert armed.changed_by == "Person"
    assert disarmed.changed_by == "Earlier"


async def test_changed_by_before_the_state_update() -> None:
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


async def test_security_value_that_is_not_an_event_is_ignored() -> None:
    """Test a malformed value is skipped and doesn't stop a valid event."""
    system = create_system(ArmedState.DISARMED)
    (panel,) = system.alarm_panels
    message = security_message("secd", ArmedState.DISARMED, "Person")
    message["da"]["seca"] = True

    system.handle_pubnub_message(message)

    assert panel.changed_by == "Person"


async def test_other_system_messages_keep_changed_by() -> None:
    """Test a system update without an event doesn't clear the value."""
    system = create_system(ArmedState.DISARMED)
    (panel,) = system.alarm_panels
    panel.update_changed_by("Person")

    system.handle_pubnub_message(
        {"t": "account_system", "op": "u", "panid": SYSTEM_ID, "da": {"s": 0}}
    )

    assert panel.changed_by == "Person"


@pytest.mark.parametrize(
    ("key", "state", "icon"),
    [
        ("seca", ArmedState.ARMED_AWAY, "armed_away"),
        ("seca", ArmedState.ARMED_STAY, "armed_stay"),
        ("secd", ArmedState.DISARMED, "disarmed"),
    ],
)
async def test_changed_by_uses_the_key_fob_name(
    key: str, state: ArmedState, icon: str
) -> None:
    """Test a key fob reported as the panel is named from the history."""
    system = create_fob_system(state, [history_event(icon)])
    (panel,) = system.alarm_panels
    listener = MagicMock()
    panel.on(UPDATE, listener)

    system.handle_pubnub_message(security_message(key, state, "panel"))
    assert panel.changed_by == "panel"
    await finish_lookup(system)

    assert panel.changed_by == FOB
    assert panel.changed_by_message == MESSAGE
    assert listener.call_count == 2


async def test_changed_by_retries_until_the_event_is_in_the_history() -> None:
    """Test the history is checked again if the event isn't there yet."""
    system = create_fob_system(ArmedState.ARMED_AWAY, [], [history_event()])
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == FOB
    assert history_mock(system).await_count == 2


@pytest.mark.parametrize(
    "event",
    [
        history_event("disarmed"),
        history_event(timestamp="2026-11-05T17:05:00.000000"),
        history_event(timestamp="not a time"),
        {"icon": "armed_away"},
    ],
)
async def test_changed_by_ignores_other_history_events(event: dict) -> None:
    """Test a history event that isn't this one doesn't change the panel."""
    system = create_fob_system(ArmedState.ARMED_AWAY, [event], [event])
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == "panel"


async def test_changed_by_skips_invalid_history_events() -> None:
    """Test an invalid history event doesn't hide the one that matches."""
    invalid = history_event(timestamp="not a time")
    system = create_fob_system(ArmedState.ARMED_AWAY, [invalid, history_event()])
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == FOB


async def test_changed_by_ignores_the_history_after_a_state_change() -> None:
    """Test a lookup can't update a panel that has since changed state."""
    system = create_fob_system(ArmedState.ARMED_AWAY, [history_event()])
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    panel.data["s"] = ArmedState.DISARMED.value
    await finish_lookup(system)

    assert panel.changed_by == "panel"
    assert panel.changed_by_message is None


async def test_changed_by_stays_the_panel_without_a_device() -> None:
    """Test an event at the panel itself gets its message and stays the panel."""
    system = create_fob_system(ArmedState.ARMED_AWAY, [history_event(device_name=None)])
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == "panel"
    assert panel.changed_by_message == MESSAGE
    history_mock(system).assert_awaited_once()


@pytest.mark.parametrize(
    "error",
    [
        VivintSkyApiError("Failed"),
        ClientError("Failed"),
        TimeoutError(),
        ValueError("Invalid JSON"),
    ],
)
async def test_changed_by_stays_the_panel_if_the_history_fails(
    error: Exception,
) -> None:
    """Test a failed history request leaves the panel as it was."""
    system = create_fob_system(ArmedState.ARMED_AWAY, error)
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == "panel"
    history_mock(system).assert_awaited_once()


@pytest.mark.parametrize(
    "message",
    [
        security_message("seca", ArmedState.ARMED_AWAY, "Person"),
        security_message("seca", ArmedState.ARMED_AWAY, "panel", uid="user"),
    ],
)
async def test_named_changed_by_keeps_its_name(message: dict) -> None:
    """Test a user keeps their name and gets the message from the history."""
    system = create_fob_system(ArmedState.ARMED_AWAY, [history_event()])
    (panel,) = system.alarm_panels
    expected = message["da"]["seca"]["n"]

    system.handle_pubnub_message(message)
    await finish_lookup(system)

    assert panel.changed_by == expected
    assert panel.changed_by_message == MESSAGE


async def test_exit_delay_skips_the_history_and_clears_the_message() -> None:
    """Test an exit delay isn't looked up, and an old message isn't kept."""
    system = create_fob_system(ArmedState.ARMING_AWAY_IN_EXIT_DELAY)
    (panel,) = system.alarm_panels
    panel.update_changed_by("Earlier", "Earlier message")

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMING_AWAY_IN_EXIT_DELAY, "panel")
    )
    await finish_lookup(system)

    assert panel.changed_by == "panel"
    assert panel.changed_by_message is None
    history_mock(system).assert_not_awaited()


async def test_newer_event_replaces_the_changed_by_lookup() -> None:
    """Test a late history result can't overwrite a newer event."""
    system = create_fob_system(
        ArmedState.ARMED_AWAY, [history_event()], [history_event()]
    )
    (panel,) = system.alarm_panels

    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )
    system.handle_pubnub_message(
        security_message("secd", ArmedState.DISARMED, "Person")
    )
    await finish_lookup(system)

    assert panel.changed_by == "Person"
    assert panel.changed_by_message is None


async def test_disconnect_cancels_the_changed_by_lookup() -> None:
    """Test disconnecting stops any history lookup."""
    account = Account("user@example.com")
    system = create_fob_system(ArmedState.ARMED_AWAY, [history_event()])
    account.systems.append(system)
    system.handle_pubnub_message(
        security_message("seca", ArmedState.ARMED_AWAY, "panel")
    )

    await account.disconnect()
    await finish_lookup(system)

    history_mock(system).assert_not_awaited()


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"his": [{"icon": "disarmed"}]}, [{"icon": "disarmed"}]),
        ({"his": []}, []),
        ({"his": None}, []),
    ],
)
async def test_get_history(response: dict, expected: list[dict]) -> None:
    """Test getting a system's history."""
    api = VivintSkyApi("user@example.com")
    get = AsyncMock(return_value=response)
    with patch.object(api, "_VivintSkyApi__get", get):
        assert await api.get_history(SYSTEM_ID, 5) == expected
    get.assert_awaited_once_with(f"{SYSTEM_ID}/1/history", params={"lim": 5})
    await api.disconnect()


@pytest.mark.parametrize(
    "response", [None, {}, {"message": "Not JSON"}, {"his": "Not a list"}]
)
async def test_get_history_with_an_invalid_response(response: dict | None) -> None:
    """Test a response that couldn't be read is reported as an error."""
    api = VivintSkyApi("user@example.com")
    with (
        patch.object(api, "_VivintSkyApi__get", AsyncMock(return_value=response)),
        pytest.raises(VivintSkyApiError),
    ):
        await api.get_history(SYSTEM_ID)
    await api.disconnect()

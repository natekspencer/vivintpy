"""Test the climate service client and the thermostats it provides."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import grpc
import jwt
import pytest
import pytest_asyncio

from vivintpy.account import Account
from vivintpy.api import VivintSkyApi
from vivintpy.const import (
    AuthUserAttribute,
    SystemAttribute,
    ThermostatAttribute,
    UserAttribute,
)
from vivintpy.devices.alarm_panel import DEVICE_DELETED, DEVICE_DISCOVERED
from vivintpy.devices.climate_thermostat import ClimateThermostat
from vivintpy.enums import (
    CapabilityCategoryType,
    CapabilityType,
    FanMode,
    HoldMode,
    OperatingMode,
    OperatingState,
)
from vivintpy.exceptions import (
    VivintSkyApiAuthenticationError,
    VivintSkyApiError,
    VivintSkyApiRateLimitError,
)
from vivintpy.proto import climate_pb2, climate_pb2_grpc
from vivintpy.system import System

SYSTEM_ID = 4000000000000001
DEVICE_URN = "urn:vivint:google:4000000000000001:device"
Component = climate_pb2.Component


def make_device(**overrides: Any) -> climate_pb2.ClimateDevice:
    """Return a Nest thermostat that is cooling toward 20 °C."""
    device = climate_pb2.ClimateDevice(
        id=DEVICE_URN,
        name="Hallway",
        is_online=True,
        temperature_units=climate_pb2.GetGlobalSettingsResponse.FAHRENHEIT,
        nest_thermostat_device=climate_pb2.NestThermostatDevice(),
        components=[
            climate_pb2.Component(
                id=f"{DEVICE_URN}:setpoints",
                setpoints=Component.Setpoints(
                    cool_setpoint=20.0,
                    heat_setpoint=15.5,
                    minimum_temperature=10.0,
                    maximum_temperature=32.2,
                ),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:temperature",
                temperature_detection=Component.TemperatureDetection(
                    current_temperature=21.5
                ),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:humidity",
                humidity_detection=Component.HumidityDetection(value=48),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:fan",
                fan_setting=Component.FanSetting(
                    modes_supported=[
                        Component.FanSetting.AUTO_LOW,
                        Component.FanSetting.FIFTEEN_MINUTE,
                        Component.FanSetting.SIXTY_MINUTE,
                    ],
                    current_mode=Component.FanSetting.AUTO_LOW,
                ),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:mode",
                operating_mode_setting=Component.OperatingModeSetting(
                    modes_supported=[
                        Component.OperatingModeSetting.HEAT,
                        Component.OperatingModeSetting.COOL,
                    ],
                    current_mode=Component.OperatingModeSetting.COOL,
                ),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:state",
                operating_state=Component.OperatingState(
                    current_state=Component.OperatingState.COOLING
                ),
            ),
            climate_pb2.Component(
                id=f"{DEVICE_URN}:hold",
                hold_mode=Component.HoldMode(mode=Component.HoldMode.PERMANENT),
            ),
        ],
    )
    device.MergeFrom(climate_pb2.ClimateDevice(**overrides))
    return device


class FakeApi:
    """Records the climate requests a thermostat sends."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, Any]] = []

    async def climate_request(self, method: str, request: Any) -> None:
        self.requests.append((method, request))

    async def get_climate_devices(self, system_id: int) -> list[Any]:
        return []


def make_system(api: Any = None) -> System:
    """Return a system with one partition and no devices."""
    return System(
        {
            "system": {
                "panid": SYSTEM_ID,
                "par": [{"panid": SYSTEM_ID, "parid": 1, "d": []}],
                "u": [],
            }
        },
        api or FakeApi(),  # type: ignore[arg-type]
        name="Home",
        is_admin=True,
    )


@pytest.fixture
def system() -> System:
    """Return a system with a fake API."""
    return make_system()


@pytest.fixture
def thermostat(system: System) -> ClimateThermostat:
    """Return the thermostat of the system."""
    system.update_climate_devices([make_device()])
    return system.alarm_panels[0].devices[0]  # type: ignore[return-value]


def test_properties(thermostat: ClimateThermostat) -> None:
    """Test the thermostat reports the state of its components."""
    assert thermostat.id == DEVICE_URN
    assert thermostat.name == "Hallway"
    assert (thermostat.manufacturer, thermostat.model) == ("Google", "Nest")
    assert thermostat.is_online
    assert thermostat.temperature == 21.5
    assert thermostat.humidity == 48
    assert thermostat.cool_set_point == 20.0
    assert thermostat.heat_set_point == 15.5
    assert thermostat.minimum_temperature == 10.0
    assert thermostat.maximum_temperature == pytest.approx(32.2)
    assert thermostat.operating_mode == OperatingMode.COOL
    assert thermostat.operating_state == OperatingState.COOLING
    assert thermostat.is_on
    assert thermostat.fan_mode == FanMode.AUTO_LOW
    assert not thermostat.is_fan_on
    assert thermostat.hold_mode == HoldMode.PERMANENT


def test_capabilities(thermostat: ClimateThermostat) -> None:
    """Test the supported fan timers are exposed as capabilities."""
    assert thermostat.capabilities == {
        CapabilityCategoryType.THERMOSTAT: [
            CapabilityType.FAN15_MINUTE,
            CapabilityType.FAN60_MINUTE,
        ]
    }


@pytest.mark.parametrize(
    ("kwargs", "method", "fields"),
    [
        (
            {ThermostatAttribute.COOL_SET_POINT: 21.0},
            "SetCoolSetpoint",
            {"celsius": 21.0, "component_id": f"{DEVICE_URN}:setpoints"},
        ),
        (
            {ThermostatAttribute.HEAT_SET_POINT: 17.0},
            "SetHeatSetpoint",
            {"celsius": 17.0, "component_id": f"{DEVICE_URN}:setpoints"},
        ),
        (
            {
                ThermostatAttribute.HEAT_SET_POINT: 17.0,
                ThermostatAttribute.COOL_SET_POINT: 22.0,
            },
            "SetTemperatureSetpoints",
            {
                "heat_celsius": 17.0,
                "cool_celsius": 22.0,
                "component_id": f"{DEVICE_URN}:setpoints",
            },
        ),
        (
            {ThermostatAttribute.FAN_MODE: FanMode.TIMER_60},
            "SetFanMode",
            {
                "mode": Component.FanSetting.SIXTY_MINUTE,
                "component_id": f"{DEVICE_URN}:fan",
            },
        ),
        (
            {ThermostatAttribute.OPERATING_MODE: OperatingMode.HEAT},
            "SetOperatingMode",
            {
                "mode": Component.OperatingModeSetting.HEAT,
                "component_id": f"{DEVICE_URN}:mode",
            },
        ),
        (
            {ThermostatAttribute.HOLD_MODE: HoldMode.BY_SCHEDULE},
            "SetHoldMode",
            {
                "mode": Component.HoldMode.BY_SCHEDULE,
                "component_id": f"{DEVICE_URN}:hold",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_set_state(
    system: System,
    thermostat: ClimateThermostat,
    kwargs: dict[str, Any],
    method: str,
    fields: dict[str, Any],
) -> None:
    """Test changing the thermostat sends the matching request."""
    await thermostat.set_state(**kwargs)

    [(sent_method, request)] = system.api.requests  # type: ignore[attr-defined]
    assert sent_method == method
    assert request.system_id == SYSTEM_ID
    assert request.device_id == DEVICE_URN
    for name, value in fields.items():
        assert getattr(request, name) == value


@pytest.mark.asyncio
async def test_set_state_rejects_unsupported(thermostat: ClimateThermostat) -> None:
    """Test attributes the service has no call for are rejected."""
    with pytest.raises(ValueError, match="Unsupported"):
        await thermostat.set_state(**{ThermostatAttribute.HUMIDITY: 40})
    with pytest.raises(ValueError, match="fan mode"):
        await thermostat.set_state(**{ThermostatAttribute.FAN_MODE: FanMode.UNKNOWN})


def test_climate_devices_are_tracked(system: System) -> None:
    """Test devices are added, updated and removed as the service reports them."""
    panel = system.alarm_panels[0]
    events: list[tuple[str, Any]] = []
    panel.on(DEVICE_DISCOVERED, lambda data: events.append(("added", data["device"])))
    panel.on(DEVICE_DELETED, lambda data: events.append(("deleted", data["device"])))

    system.update_climate_devices([make_device()])
    [device] = panel.devices
    assert events == [("added", device)]

    updates: list[dict] = []
    device.on("update", updates.append)
    system.update_climate_devices([make_device(name="Hallway 2")], [])
    assert panel.devices == [device]
    assert device.name == "Hallway 2"
    assert updates

    system.update_climate_devices([], [DEVICE_URN])
    assert panel.devices == []
    assert events[-1] == ("deleted", device)


def test_partial_update_keeps_other_components(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test an update that carries only some components leaves the others in place."""
    update = climate_pb2.ClimateDevice(
        id=DEVICE_URN,
        name="Hallway",
        is_online=True,
        components=[
            climate_pb2.Component(
                id=f"{DEVICE_URN}:setpoints",
                setpoints=Component.Setpoints(cool_setpoint=21.0, heat_setpoint=15.5),
            )
        ],
    )

    system.update_climate_devices([update])

    assert thermostat.cool_set_point == 21.0
    assert thermostat.temperature == 21.5
    assert thermostat.operating_state == OperatingState.COOLING
    assert len(thermostat._device.components) == 7


def test_panel_thermostat_is_not_duplicated(system: System) -> None:
    """Test a thermostat the panel already reports is not added a second time."""
    from vivintpy.devices.thermostat import Thermostat

    panel = system.alarm_panels[0]
    panel.devices.append(
        Thermostat({"_id": 12, "t": "thermostat_device", "panid": SYSTEM_ID}, panel)
    )

    system.update_climate_devices([make_device(id=f"urn:vivint:panel:{SYSTEM_ID}:12")])

    assert len(panel.devices) == 1


class Servicer(climate_pb2_grpc.ClimatePublicServicer):
    """A climate service that records what it is asked."""

    def __init__(self) -> None:
        self.metadata: list[dict[str, str]] = []
        self.reject_first = False

    async def GetClimateDevices(self, request: Any, context: Any) -> Any:
        self.metadata.append(dict(context.invocation_metadata()))
        if self.reject_first and len(self.metadata) == 1:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "expired")
        if request.system_id != SYSTEM_ID:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, "wrong system")
        return climate_pb2.GetClimateDevicesResponse(climate_devices=[make_device()])

    async def SetCoolSetpoint(self, request: Any, context: Any) -> Any:
        await context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "rate limit exceeded")

    async def GetClimateDevicesStreaming(
        self, request: Any, context: Any
    ) -> AsyncIterator[Any]:
        self.metadata.append(dict(context.invocation_metadata()))
        if self.reject_first and len(self.metadata) == 1:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "expired")
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            climate_devices=[make_device()]
        )
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            deleted_device_ids=[DEVICE_URN]
        )


@pytest_asyncio.fixture
async def service(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[Servicer]:
    """Run a climate service and point the API at it."""
    server = grpc.aio.server()
    servicer = Servicer()
    climate_pb2_grpc.add_ClimatePublicServicer_to_server(servicer, server)  # type: ignore[no-untyped-call]
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    monkeypatch.setattr(
        grpc.aio,
        "secure_channel",
        lambda *_args, **_kwargs: grpc.aio.insecure_channel(f"127.0.0.1:{port}"),
    )
    yield servicer
    await server.stop(None)


def make_api() -> VivintSkyApi:
    """Return an API that holds a valid session."""
    api = VivintSkyApi("user", "password", client_session=MagicMock())
    api._VivintSkyApi__token = {  # type: ignore[attr-defined]
        "access_token": "access",
        "id_token": jwt.encode({"exp": int(time.time()) + 3600}, "k" * 32),
    }
    return api


@pytest.mark.asyncio
async def test_get_climate_devices(service: Servicer) -> None:
    """Test devices are requested with the access token as a bearer token."""
    api = make_api()

    devices = await api.get_climate_devices(SYSTEM_ID)

    assert [device.id for device in devices] == [DEVICE_URN]
    assert service.metadata[0]["authorization"] == "Bearer access"


@pytest.mark.asyncio
async def test_climate_error(service: Servicer) -> None:
    """Test a refused call raises a library error."""
    with pytest.raises(VivintSkyApiError, match="PERMISSION_DENIED: wrong system"):
        await make_api().get_climate_devices(SYSTEM_ID + 1)


@pytest.mark.asyncio
async def test_climate_rate_limit(service: Servicer) -> None:
    """Test a refused change because of too many changes is reported as such."""
    request = climate_pb2.SetCoolSetpointRequest(system_id=SYSTEM_ID, celsius=21.0)

    with pytest.raises(VivintSkyApiRateLimitError, match="rate limit"):
        await make_api().climate_request("SetCoolSetpoint", request)


@pytest.mark.asyncio
async def test_climate_request_reauthenticates(
    service: Servicer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test an unauthenticated call signs in again and is retried once."""
    service.reject_first = True
    api = make_api()
    logins = []

    async def login(*_args: Any) -> None:
        logins.append(True)
        api._VivintSkyApi__token = {  # type: ignore[attr-defined]
            "access_token": "fresh",
            "id_token": jwt.encode({"exp": int(time.time()) + 3600}, "k" * 32),
        }

    async def authuser() -> dict:
        return {"u": {}}

    monkeypatch.setattr(api, "_VivintSkyApi__get_vivintsky_session", login)
    monkeypatch.setattr(api, "get_authuser_data", authuser)
    api._VivintSkyApi__has_custom_client_session = True  # type: ignore[attr-defined]

    assert await api.get_climate_devices(SYSTEM_ID)
    assert logins == [True]
    assert [m["authorization"] for m in service.metadata] == [
        "Bearer access",
        "Bearer fresh",
    ]


@pytest.mark.asyncio
async def test_stream_reauthenticates(
    service: Servicer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test a stream rejected before any update signs in again and retries."""
    service.reject_first = True
    api = make_api()
    logins = []

    async def reauthenticate() -> None:
        logins.append(True)

    monkeypatch.setattr(api, "_reauthenticate", reauthenticate)

    updates = [update async for update in api.stream_climate_devices(SYSTEM_ID)]
    assert logins == [True]
    assert len(updates) == 2


@pytest.mark.asyncio
async def test_stream_climate_devices(service: Servicer) -> None:
    """Test the stream names the system in a header and yields each update."""
    updates = [update async for update in make_api().stream_climate_devices(SYSTEM_ID)]

    assert [len(u.climate_devices) for u in updates] == [1, 0]
    assert list(updates[1].deleted_device_ids) == [DEVICE_URN]
    assert service.metadata[0]["x-viv-system-id"] == str(SYSTEM_ID)


class StreamApi(FakeApi):
    """An API whose stream reports a thermostat and then its removal."""

    def __init__(self) -> None:
        super().__init__()
        self.remove = asyncio.Event()

    async def stream_climate_devices(
        self, system_id: int
    ) -> AsyncIterator[climate_pb2.GetClimateDevicesStreamingResponse]:
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            climate_devices=[make_device()]
        )
        await self.remove.wait()
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            deleted_device_ids=[DEVICE_URN]
        )
        await asyncio.Event().wait()


async def wait_for(condition: Callable[[], bool]) -> None:
    """Wait until the condition holds."""
    async with asyncio.timeout(5):
        while not condition():
            await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_system_applies_stream() -> None:
    """Test a system keeps its thermostats in step with the stream."""
    api = StreamApi()
    system = make_system(api)
    devices = system.alarm_panels[0].devices

    system.start_climate_updates()
    try:
        await wait_for(lambda: len(devices) == 1)
        assert system.climate_updates_running
        api.remove.set()
        await wait_for(lambda: not devices)
    finally:
        await system.stop_climate_updates()

    assert not system.climate_updates_running


class FailingStreamApi(FakeApi):
    """An API whose stream fails with an unexpected error, then recovers."""

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    async def stream_climate_devices(
        self, system_id: int
    ) -> AsyncIterator[climate_pb2.GetClimateDevicesStreamingResponse]:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("token renewal failed")
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            climate_devices=[make_device()]
        )
        await asyncio.sleep(3600)


@pytest.mark.asyncio
async def test_stream_survives_unexpected_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the stream task keeps retrying after any error."""
    monkeypatch.setattr("vivintpy.system.CLIMATE_RETRY_MIN", 0)
    system = make_system(FailingStreamApi())
    system.start_climate_updates()
    try:
        await wait_for(lambda: len(system.alarm_panels[0].devices) == 1)
    finally:
        await system.stop_climate_updates()


def test_unknown_enum_values_fall_back(thermostat: ClimateThermostat) -> None:
    """Test enum values the proto doesn't define read as unknown."""
    update = make_device()
    for component in update.components:
        kind = component.WhichOneof("value")
        if kind == "fan_setting":
            component.fan_setting.current_mode = 99
            component.fan_setting.modes_supported.append(99)
        elif kind == "operating_mode_setting":
            component.operating_mode_setting.current_mode = 99
        elif kind == "hold_mode":
            component.hold_mode.mode = 99
        elif kind == "operating_state":
            component.operating_state.current_state = 99

    thermostat.update_device(update)

    assert thermostat.fan_mode == FanMode.UNKNOWN
    assert thermostat.operating_mode == OperatingMode.UNKNOWN
    assert thermostat.hold_mode == HoldMode.UNKNOWN
    assert thermostat.operating_state == OperatingState.UNKNOWN
    assert thermostat.capabilities[CapabilityCategoryType.THERMOSTAT]


def test_component_only_update_keeps_device_fields(
    thermostat: ClimateThermostat,
) -> None:
    """Test an update without name, online flag or details leaves them as they were."""
    thermostat.update_device(
        climate_pb2.ClimateDevice(
            id=DEVICE_URN,
            components=[
                climate_pb2.Component(
                    id=f"{DEVICE_URN}:temperature",
                    temperature_detection=Component.TemperatureDetection(
                        current_temperature=22.0
                    ),
                )
            ],
        )
    )

    assert thermostat.temperature == 22.0
    assert thermostat.name == "Hallway"
    assert thermostat.is_online
    assert (thermostat.manufacturer, thermostat.model) == ("Google", "Nest")
    assert thermostat._device.WhichOneof("details") == "nest_thermostat_device"


def test_unset_set_points_are_none(system: System) -> None:
    """Test set points and limits the service leaves unset read as `None`."""
    device = make_device()
    for component in device.components:
        if component.WhichOneof("value") == "setpoints":
            component.setpoints.maximum_temperature = 0
            component.setpoints.cool_setpoint = 0
    system.update_climate_devices([device])
    thermostat = system.alarm_panels[0].devices[0]

    assert thermostat.maximum_temperature is None  # type: ignore[attr-defined]
    assert thermostat.cool_set_point is None  # type: ignore[attr-defined]
    assert thermostat.heat_set_point == 15.5  # type: ignore[attr-defined]


def test_snapshot_removes_missing_thermostats(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test a full snapshot drops thermostats it no longer lists."""
    system.update_climate_devices([], snapshot=True)

    assert system.alarm_panels[0].devices == []


@pytest.mark.asyncio
async def test_set_state_validates_before_sending(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test an unsupported value is rejected before any request is sent."""
    with pytest.raises(ValueError, match="fan mode"):
        await thermostat.set_state(
            **{
                ThermostatAttribute.COOL_SET_POINT: 21.0,
                ThermostatAttribute.FAN_MODE: FanMode.UNKNOWN,
            }
        )

    assert system.api.requests == []  # type: ignore[attr-defined]


def test_fan_on_is_reported_as_its_own_state(thermostat: ClimateThermostat) -> None:
    """Test a thermostat that is only running its fan is not reported as idle."""
    thermostat._component("operating_state").current_state = (  # type: ignore[union-attr]
        Component.OperatingState.FAN_ON
    )

    assert thermostat.operating_state == OperatingState.FAN_ON
    assert thermostat.is_on


@pytest.mark.asyncio
async def test_climate_response_is_not_logged(
    service: Servicer, caplog: pytest.LogCaptureFixture
) -> None:
    """Test the debug log has no thermostat details."""
    api = make_api()

    with caplog.at_level("DEBUG", logger="vivintpy.api"):
        await api.get_climate_devices(SYSTEM_ID)

    assert "GetClimateDevices" in caplog.text
    assert "Hallway" not in caplog.text
    assert DEVICE_URN not in caplog.text


@pytest.mark.asyncio
async def test_reconnect_restarts_climate_updates() -> None:
    """Test an account that reconnects starts the streams of the systems it kept."""
    account = Account("user", client_session=MagicMock())
    account._Account__subscribe_for_realtime_updates = True  # type: ignore[attr-defined]
    system = MagicMock()
    system.id = SYSTEM_ID
    system.refresh = AsyncMock()
    account.systems = [system]

    await account.refresh(
        {
            AuthUserAttribute.USERS: {
                UserAttribute.SYSTEM: [{SystemAttribute.PANEL_ID: SYSTEM_ID}]
            }
        }
    )

    system.refresh.assert_awaited_once()
    system.start_climate_updates.assert_called_once_with()


class SnapshotApi(FakeApi):
    """An API whose snapshot is held back until the test releases it."""

    def __init__(self) -> None:
        super().__init__()
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.loads = 0

    async def get_climate_devices(self, system_id: int) -> list[Any]:
        self.loads += 1
        self.started.set()
        snapshot = [make_device()]
        await self.release.wait()
        return snapshot


@pytest.mark.asyncio
async def test_snapshot_does_not_undo_a_deletion_from_the_stream() -> None:
    """Test a thermostat the stream deletes while a snapshot loads stays deleted."""
    api = SnapshotApi()
    system = make_system(api)
    system.update_climate_devices([make_device()])
    devices = system.alarm_panels[0].devices

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([], [DEVICE_URN])
    assert not devices
    api.release.set()
    await load

    assert not devices


@pytest.mark.asyncio
async def test_snapshot_keeps_a_thermostat_the_stream_recreates() -> None:
    """Test a thermostat deleted and then reported again during a load is kept."""
    api = SnapshotApi()
    system = make_system(api)
    system.update_climate_devices([make_device()])
    devices = system.alarm_panels[0].devices

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([], [DEVICE_URN])
    system.update_climate_devices([make_device()])
    api.release.set()
    await load

    assert len(devices) == 1


@pytest.mark.asyncio
async def test_stop_clears_the_stream_connected_flag() -> None:
    """Test updates that are started again aren't reported as running early."""
    api = StreamApi()
    system = make_system(api)

    system.start_climate_updates()
    await wait_for(lambda: system.climate_updates_running)
    await system.stop_climate_updates()
    system.start_climate_updates()
    try:
        assert not system.climate_updates_running
    finally:
        await system.stop_climate_updates()


@pytest.mark.asyncio
async def test_a_later_command_resets_the_refresh_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test each command waits out the delay again before thermostats reload."""
    monkeypatch.setattr("vivintpy.system.CLIMATE_REFRESH_DELAY", 0.2)
    api = SnapshotApi()
    api.release.set()
    system = make_system(api)

    system.request_climate_refresh()
    await asyncio.sleep(0.12)
    system.request_climate_refresh()
    await asyncio.sleep(0.12)
    assert api.loads == 0

    await wait_for(lambda: api.loads == 1)
    await system.stop_climate_updates()


@pytest.mark.asyncio
async def test_a_command_during_a_load_gets_another_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a command that completes while thermostats load is followed by a load."""
    monkeypatch.setattr("vivintpy.system.CLIMATE_REFRESH_DELAY", 0.01)
    api = SnapshotApi()
    system = make_system(api)

    system.request_climate_refresh()
    await api.started.wait()
    system.request_climate_refresh()
    api.release.set()

    await wait_for(lambda: api.loads == 2)
    await system.stop_climate_updates()


def test_climate_thermostat_is_removed_when_its_panel_thermostat_appears(
    system: System,
) -> None:
    """Test the panel's own thermostat replaces a climate twin found earlier."""
    from vivintpy.devices.thermostat import Thermostat

    panel = system.alarm_panels[0]
    deleted: list[dict] = []
    panel.on(DEVICE_DELETED, deleted.append)
    twin = make_device(id=f"urn:vivint:panel:{SYSTEM_ID}:12")
    system.update_climate_devices([twin])
    assert isinstance(panel.devices[0], ClimateThermostat)

    panel_thermostat = Thermostat(
        {"_id": 12, "t": "thermostat_device", "panid": SYSTEM_ID}, panel
    )
    panel.devices.append(panel_thermostat)
    system.update_climate_devices([twin])

    assert panel.devices == [panel_thermostat]
    assert len(deleted) == 1


def test_snapshot_drops_a_removed_component(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test a full snapshot replaces the components instead of merging them."""
    assert thermostat.fan_mode is not None
    snapshot = make_device()
    kept = [c for c in snapshot.components if c.WhichOneof("value") != "fan_setting"]
    del snapshot.components[:]
    snapshot.components.extend(kept)

    system.update_climate_devices([snapshot], snapshot=True)

    assert thermostat._component("fan_setting") is None
    assert thermostat._component("setpoints") is not None


def test_partial_update_still_merges_components(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test an update from the stream keeps the components it doesn't carry."""
    update = climate_pb2.ClimateDevice(id=DEVICE_URN)

    system.update_climate_devices([update])

    assert thermostat._component("fan_setting") is not None


@pytest.mark.asyncio
async def test_snapshot_keeps_a_thermostat_the_stream_adds() -> None:
    """Test a snapshot taken before the stream adds a thermostat doesn't remove it."""
    api = SnapshotApi()
    system = make_system(api)
    devices = system.alarm_panels[0].devices

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    other = make_device(id=f"urn:vivint:google:{SYSTEM_ID}:other", name="Bedroom")
    system.update_climate_devices([other])
    api.release.set()
    await load

    assert sorted(device.id for device in devices) == sorted([DEVICE_URN, other.id])
    assert next(d for d in devices if d.id == other.id).name == "Bedroom"


@pytest.mark.asyncio
async def test_snapshot_does_not_overwrite_a_newer_stream_update() -> None:
    """Test a stale snapshot doesn't undo a change the stream reported meanwhile."""
    api = SnapshotApi()
    system = make_system(api)
    system.update_climate_devices([make_device()])
    thermostat = system.alarm_panels[0].devices[0]

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([make_device(name="Renamed")])
    api.release.set()
    await load

    assert thermostat.name == "Renamed"


class ReconnectingStreamApi(FakeApi):
    """An API whose stream lists two thermostats and, after dropping, only one."""

    def __init__(self) -> None:
        super().__init__()
        self.calls = 0
        self.other = make_device(id=f"urn:vivint:google:{SYSTEM_ID}:other")

    async def stream_climate_devices(
        self, system_id: int
    ) -> AsyncIterator[climate_pb2.GetClimateDevicesStreamingResponse]:
        self.calls += 1
        if self.calls == 1:
            yield climate_pb2.GetClimateDevicesStreamingResponse(
                climate_devices=[make_device(), self.other]
            )
            raise RuntimeError("connection dropped")
        yield climate_pb2.GetClimateDevicesStreamingResponse(
            climate_devices=[make_device()]
        )
        await asyncio.sleep(3600)


@pytest.mark.asyncio
async def test_first_stream_message_removes_what_went_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a thermostat deleted while the stream was down is removed on reconnect."""
    monkeypatch.setattr("vivintpy.system.CLIMATE_RETRY_MIN", 0)
    api = ReconnectingStreamApi()
    system = make_system(api)
    devices = system.alarm_panels[0].devices

    system.start_climate_updates()
    try:
        await wait_for(lambda: api.calls == 2 and len(devices) == 1)
    finally:
        await system.stop_climate_updates()

    assert [device.id for device in devices] == [DEVICE_URN]


@pytest.mark.asyncio
async def test_first_stream_message_drops_a_removed_component(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test a full listing replaces the components, and later messages merge."""
    listing = make_device()
    kept = [c for c in listing.components if c.WhichOneof("value") != "fan_setting"]
    del listing.components[:]
    listing.components.extend(kept)

    system.update_climate_devices([listing], snapshot=True)
    assert thermostat._component("fan_setting") is None

    system.update_climate_devices([climate_pb2.ClimateDevice(id=DEVICE_URN)])
    assert thermostat._component("setpoints") is not None


@pytest.mark.asyncio
async def test_authentication_errors_from_a_load_are_raised() -> None:
    """Test a failed sign-in isn't hidden by the load."""

    class Api(FakeApi):
        async def get_climate_devices(self, system_id: int) -> list[Any]:
            raise VivintSkyApiAuthenticationError("rejected")

    with pytest.raises(VivintSkyApiAuthenticationError):
        await make_system(Api()).load_climate_devices()


@pytest.mark.asyncio
async def test_other_errors_from_a_load_are_logged() -> None:
    """Test an outage during a load leaves the thermostats as they were."""

    class Api(FakeApi):
        async def get_climate_devices(self, system_id: int) -> list[Any]:
            raise VivintSkyApiError("outage")

    system = make_system(Api())
    system.update_climate_devices([make_device()])

    await system.load_climate_devices()

    assert len(system.alarm_panels[0].devices) == 1


@pytest.mark.asyncio
async def test_loads_do_not_overlap() -> None:
    """Test a load fetches only after the previous one has applied its result."""

    class Api(FakeApi):
        def __init__(self) -> None:
            super().__init__()
            self.active = 0
            self.most = 0

        async def get_climate_devices(self, system_id: int) -> list[Any]:
            self.active += 1
            self.most = max(self.most, self.active)
            await asyncio.sleep(0.01)
            self.active -= 1
            return [make_device()]

    api = Api()
    system = make_system(api)

    await asyncio.gather(system.load_climate_devices(), system.load_climate_devices())

    assert api.most == 1


@pytest.mark.asyncio
async def test_snapshot_fills_in_a_thermostat_the_stream_reported_in_part() -> None:
    """Test a snapshot supplies what a partial stream update left out."""
    api = SnapshotApi()
    system = make_system(api)
    partial = climate_pb2.ClimateDevice(
        id=DEVICE_URN,
        name="Hallway",
        components=[
            climate_pb2.Component(
                id=f"{DEVICE_URN}:temperature",
                temperature_detection=Component.TemperatureDetection(
                    current_temperature=25.0
                ),
            )
        ],
    )

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([partial])
    api.release.set()
    await load

    thermostat = system.alarm_panels[0].devices[0]
    assert thermostat.temperature == 25.0  # type: ignore[attr-defined]
    assert thermostat.heat_set_point == 15.5  # type: ignore[attr-defined]


def test_unset_temperature_and_humidity_are_none(
    system: System, thermostat: ClimateThermostat
) -> None:
    """Test a detection component with no value isn't reported as zero."""
    thermostat._component("temperature_detection").current_temperature = 0.0  # type: ignore[union-attr]
    thermostat._component("humidity_detection").value = 0  # type: ignore[union-attr]

    assert thermostat.temperature is None
    assert thermostat.humidity is None


@pytest.mark.asyncio
async def test_subscribing_later_starts_climate_updates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test subscribing for realtime updates after connecting starts the streams."""
    monkeypatch.setattr("vivintpy.account.PubNubAsyncio", MagicMock())
    account = Account("user", client_session=MagicMock())
    system = MagicMock()
    account.systems = [system]

    await account.subscribe_for_realtime_updates(
        {
            AuthUserAttribute.USERS: {
                UserAttribute.ID: "abc",
                UserAttribute.MESSAGE_BROADCAST_CHANNEL: "channel",
            }
        }
    )

    system.start_climate_updates.assert_called_once_with()


@pytest.mark.asyncio
async def test_snapshot_supplies_the_identity_a_partial_update_lacked() -> None:
    """Test a thermostat first reported without a name gets one from the snapshot."""
    api = SnapshotApi()
    system = make_system(api)
    partial = climate_pb2.ClimateDevice(
        id=DEVICE_URN,
        components=[
            climate_pb2.Component(
                id=f"{DEVICE_URN}:temperature",
                temperature_detection=Component.TemperatureDetection(
                    current_temperature=25.0
                ),
            )
        ],
    )

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([partial])
    api.release.set()
    await load

    thermostat = system.alarm_panels[0].devices[0]
    assert thermostat.name == "Hallway"
    assert thermostat.is_online  # type: ignore[attr-defined]
    assert thermostat.manufacturer == "Google"
    assert thermostat.temperature == 25.0  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_load_is_discarded_after_a_full_listing_from_the_stream() -> None:
    """Test an older response doesn't add back what a newer full listing omits."""
    api = SnapshotApi()
    system = make_system(api)
    devices = system.alarm_panels[0].devices

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([], snapshot=True)
    api.release.set()
    await load

    assert not devices


@pytest.mark.asyncio
async def test_load_does_not_restore_a_component_a_full_listing_dropped() -> None:
    """Test an older response doesn't bring back a component the stream removed."""
    api = SnapshotApi()
    system = make_system(api)
    system.update_climate_devices([make_device()])
    thermostat = system.alarm_panels[0].devices[0]
    listing = make_device()
    kept = [c for c in listing.components if c.WhichOneof("value") != "fan_setting"]
    del listing.components[:]
    listing.components.extend(kept)

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([listing], snapshot=True)
    api.release.set()
    await load

    assert thermostat._component("fan_setting") is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_disconnect_stops_a_refresh_from_restarting_the_streams() -> None:
    """Test a refresh that finishes after a disconnect doesn't start climate streams."""

    class Api:
        async def disconnect(self) -> None:
            """Do nothing."""

    account = Account("user", client_session=MagicMock())
    account._api = Api()  # type: ignore[assignment]
    account._Account__subscribe_for_realtime_updates = True  # type: ignore[attr-defined]
    system = MagicMock()
    system.id = SYSTEM_ID
    system.refresh = AsyncMock()
    system.stop_climate_updates = AsyncMock()
    system.disconnect_dvrs = AsyncMock()
    account.systems = [system]

    await account.disconnect()
    await account.refresh(
        {
            AuthUserAttribute.USERS: {
                UserAttribute.SYSTEM: [{SystemAttribute.PANEL_ID: SYSTEM_ID}]
            }
        }
    )

    system.start_climate_updates.assert_not_called()


@pytest.mark.asyncio
async def test_snapshot_does_not_fill_a_recreated_thermostat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a thermostat deleted and recreated during a load gets a fresh load."""
    monkeypatch.setattr("vivintpy.system.CLIMATE_REFRESH_DELAY", 0.01)
    api = SnapshotApi()
    system = make_system(api)
    system.update_climate_devices([make_device()])
    thermostat = system.alarm_panels[0].devices[0]
    replacement = climate_pb2.ClimateDevice(
        id=DEVICE_URN,
        name="Hallway",
        components=[
            climate_pb2.Component(
                id=f"{DEVICE_URN}:temperature",
                temperature_detection=Component.TemperatureDetection(
                    current_temperature=25.0
                ),
            )
        ],
    )

    load = asyncio.create_task(system.load_climate_devices())
    await api.started.wait()
    system.update_climate_devices([], [DEVICE_URN])
    system.update_climate_devices([replacement])
    api.release.set()
    await load

    recreated = system.alarm_panels[0].devices[0]
    assert recreated is not thermostat
    assert recreated._component("fan_setting") is None  # type: ignore[attr-defined]
    await wait_for(lambda: recreated._component("fan_setting") is not None)  # type: ignore[attr-defined]
    await system.stop_climate_updates()


@pytest.mark.asyncio
async def test_pending_subscription_does_not_outlive_a_disconnect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a subscription that is waiting for the account's data gives up."""
    pubnub = MagicMock()
    monkeypatch.setattr("vivintpy.account.PubNubAsyncio", pubnub)
    release = asyncio.Event()

    class Api:
        async def get_authuser_data(self) -> dict:
            """Return the user's data once released."""
            await release.wait()
            return {
                AuthUserAttribute.USERS: {
                    UserAttribute.ID: "abc",
                    UserAttribute.MESSAGE_BROADCAST_CHANNEL: "channel",
                }
            }

        async def disconnect(self) -> None:
            """Do nothing."""

    account = Account("user", client_session=MagicMock())
    account._api = Api()  # type: ignore[assignment]
    system = MagicMock()
    system.stop_climate_updates = AsyncMock()
    system.disconnect_dvrs = AsyncMock()
    account.systems = [system]

    subscription = asyncio.create_task(account.subscribe_for_realtime_updates())
    await asyncio.sleep(0)
    await account.disconnect()
    release.set()
    await subscription

    pubnub.assert_not_called()
    system.start_climate_updates.assert_not_called()

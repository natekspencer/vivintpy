"""Test the climate service client and the thermostats it provides."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable
from typing import Any
from unittest.mock import MagicMock

import grpc
import jwt
import pytest
import pytest_asyncio

from vivintpy.api import VivintSkyApi
from vivintpy.const import ThermostatAttribute
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
from vivintpy.exceptions import VivintSkyApiError, VivintSkyApiRateLimitError
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
    """Test an unauthenticated call is retried once with a fresh session."""
    service.reject_first = True
    api = make_api()
    connected = []

    async def connect() -> dict:
        connected.append(True)
        return {}

    monkeypatch.setattr(api, "connect", connect)

    assert await api.get_climate_devices(SYSTEM_ID)
    assert connected == [True]
    assert len(service.metadata) == 2


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
        assert system.climate_updates_running
        await wait_for(lambda: len(devices) == 1)
        api.remove.set()
        await wait_for(lambda: not devices)
    finally:
        await system.stop_climate_updates()

    assert not system.climate_updates_running

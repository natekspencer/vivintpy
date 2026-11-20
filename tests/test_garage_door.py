"""Test the garage door."""

import logging
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest
from aiohttp import ClientResponseError

from vivintpy.api import AUTH_ENDPOINT, VivintSkyApi
from vivintpy.devices.garage_door import GarageDoor
from vivintpy.enums import GarageDoorState
from vivintpy.exceptions import (
    VivintSkyApiAuthenticationError,
    VivintSkyApiError,
    VivintSkyGrpcError,
)
from vivintpy.proto import garage_pb2
from vivintpy.system import System

PANEL_ID = 8070719956882364
PARTITION_ID = 1
DEVICE_ID = 45
VENDOR_ID = "urn:vivint:panel:8070719956882364:45"


def listed(vendor_device_id: str, name: str) -> garage_pb2.GarageDoorDevice:
    """Return a door as the garage service lists it."""
    return garage_pb2.GarageDoorDevice(vendor_device_id=vendor_device_id, name=name)


def create_garage_door(
    *doors: garage_pb2.GarageDoorDevice,
) -> tuple[GarageDoor, MagicMock]:
    """Return a garage door on a panel and the mocked API it uses.

    The garage service lists `doors`, or just this door by its panel id.
    """
    api = MagicMock()
    api.get_garage_doors = AsyncMock(
        return_value=list(doors) or [listed(VENDOR_ID, "Garage")]
    )
    api.open_garage_door = AsyncMock()
    api.close_garage_door = AsyncMock()
    api.set_garage_door_state = AsyncMock()
    system = System(
        {
            "system": {
                "panid": PANEL_ID,
                "u": [],
                "par": [
                    {
                        "panid": PANEL_ID,
                        "parid": PARTITION_ID,
                        "s": 1,
                        "d": [
                            {
                                "_id": DEVICE_ID,
                                "t": "garage_door_device",
                                "n": "Garage",
                                "s": GarageDoorState.CLOSED.value,
                                "ol": True,
                            }
                        ],
                    }
                ],
            }
        },
        api,
        name="Home",
        is_admin=True,
    )
    door = system.alarm_panels[0].devices[0]
    assert isinstance(door, GarageDoor)
    return door, api


def grpc_error(code: grpc.StatusCode) -> VivintSkyGrpcError:
    """Return the error the API raises when the garage service fails."""
    return VivintSkyGrpcError("OpenGarageDoor", code, "rejected")


async def test_open_uses_garage_service() -> None:
    """Opening a door goes through the garage service, not the door endpoint."""
    door, api = create_garage_door()
    await door.open()
    api.get_garage_doors.assert_awaited_once_with(PANEL_ID)
    api.open_garage_door.assert_awaited_once_with(PANEL_ID, VENDOR_ID)
    api.set_garage_door_state.assert_not_awaited()


async def test_close_uses_garage_service() -> None:
    """Closing a door goes through the garage service, not the door endpoint."""
    door, api = create_garage_door()
    await door.close()
    api.close_garage_door.assert_awaited_once_with(PANEL_ID, VENDOR_ID)
    api.set_garage_door_state.assert_not_awaited()


@pytest.mark.parametrize("failing", ["get_garage_doors", "open_garage_door"])
async def test_unimplemented_falls_back_to_door_endpoint(failing: str) -> None:
    """A garage service without the method falls back to the door endpoint."""
    door, api = create_garage_door()
    getattr(api, failing).side_effect = grpc_error(grpc.StatusCode.UNIMPLEMENTED)
    await door.open()
    api.set_garage_door_state.assert_awaited_once_with(
        PANEL_ID, PARTITION_ID, DEVICE_ID, GarageDoorState.OPENING
    )


async def test_other_errors_do_not_fall_back() -> None:
    """A rejected command is raised instead of retried on the door endpoint."""
    door, api = create_garage_door()
    api.open_garage_door.side_effect = grpc_error(grpc.StatusCode.PERMISSION_DENIED)
    with pytest.raises(VivintSkyGrpcError, match="PERMISSION_DENIED"):
        await door.open()
    api.set_garage_door_state.assert_not_awaited()


async def test_other_states_use_door_endpoint() -> None:
    """States the garage service can't set still go to the door endpoint."""
    door, api = create_garage_door()
    await door.set_state(GarageDoorState.STOPPED)
    api.get_garage_doors.assert_not_awaited()
    api.open_garage_door.assert_not_awaited()
    api.close_garage_door.assert_not_awaited()
    api.set_garage_door_state.assert_awaited_once_with(
        PANEL_ID, PARTITION_ID, DEVICE_ID, GarageDoorState.STOPPED
    )


@pytest.mark.parametrize(
    ("doors", "expected"),
    [
        pytest.param(
            [
                listed(f"urn:vivint:panel:{PANEL_ID}:450", "Garage"),
                listed(VENDOR_ID, "Shop"),
            ],
            VENDOR_ID,
            id="panel door by id over name",
        ),
        pytest.param(
            [
                listed(f"urn:vivint:myq:{PANEL_ID}:7", "Garage"),
                listed(f"urn:vivint:myq:{PANEL_ID}:45", "Shop"),
            ],
            f"urn:vivint:myq:{PANEL_ID}:45",
            id="myq door by id over name",
        ),
        pytest.param(
            [
                listed("urn:vivint:myq:1:45", "Shop"),
                listed("urn:vivint:myq:2:9", "Garage"),
            ],
            "urn:vivint:myq:2:9",
            id="device id on another panel falls back to name",
        ),
        pytest.param(
            [listed("myq-abc123", "  garage "), listed("myq-def456", "Shop")],
            "myq-abc123",
            id="name",
        ),
    ],
)
async def test_door_is_matched_to_the_listed_id(
    doors: list[garage_pb2.GarageDoorDevice], expected: str
) -> None:
    """The command uses the id the garage service lists for this door."""
    door, api = create_garage_door(*doors)
    await door.open()
    api.open_garage_door.assert_awaited_once_with(PANEL_ID, expected)


async def test_listed_id_is_kept() -> None:
    """Later commands reuse the door's id without listing the doors again."""
    door, api = create_garage_door()
    await door.open()
    await door.close()
    api.get_garage_doors.assert_awaited_once_with(PANEL_ID)
    api.open_garage_door.assert_awaited_once_with(PANEL_ID, VENDOR_ID)
    api.close_garage_door.assert_awaited_once_with(PANEL_ID, VENDOR_ID)


async def test_unmatched_door_is_looked_up_again() -> None:
    """A door that wasn't matched is looked up again on the next command."""
    door, api = create_garage_door()
    api.get_garage_doors.return_value = []
    with pytest.raises(VivintSkyApiError):
        await door.open()
    api.get_garage_doors.return_value = [listed(VENDOR_ID, "Garage")]
    await door.open()
    assert api.get_garage_doors.await_count == 2
    api.open_garage_door.assert_awaited_once_with(PANEL_ID, VENDOR_ID)


@pytest.mark.parametrize(
    "doors",
    [
        pytest.param([listed("myq-abc123", "Shop")], id="no match"),
        pytest.param(
            [listed("myq-abc123", "Garage"), listed("myq-def456", "Garage")],
            id="two doors with the name",
        ),
        pytest.param([], id="no doors"),
    ],
)
async def test_unmatched_door_is_not_sent(
    doors: list[garage_pb2.GarageDoorDevice], caplog: pytest.LogCaptureFixture
) -> None:
    """A door the service doesn't clearly list raises and logs what was listed."""
    door, api = create_garage_door()
    api.get_garage_doors.return_value = doors
    caplog.set_level(logging.DEBUG, logger="vivintpy.devices.garage_door")
    with pytest.raises(VivintSkyApiError, match=r"matching Garage \(45\)"):
        await door.open()
    api.open_garage_door.assert_not_awaited()
    api.set_garage_door_state.assert_not_awaited()
    assert "Garage service lists" in caplog.text


def create_api() -> VivintSkyApi:
    """Return an API with a valid session."""
    api = VivintSkyApi("user", refresh_token="refresh", client_session=MagicMock())
    api._VivintSkyApi__token = {"access_token": "access"}  # type: ignore[attr-defined]
    return api


class AioRpcError(grpc.aio.AioRpcError):
    """An RPC error that can be built without a call."""

    def __init__(self, code: grpc.StatusCode, details: str) -> None:
        """Initialize the error."""
        super().__init__(code, grpc.aio.Metadata(), grpc.aio.Metadata(), details)


@pytest.mark.parametrize(
    ("method", "request_type", "rpc"),
    [
        ("open_garage_door", garage_pb2.OpenGarageDoorRequest, "OpenGarageDoor"),
        ("close_garage_door", garage_pb2.CloseGarageDoorRequest, "CloseGarageDoor"),
    ],
)
async def test_api_sends_command(
    method: str,
    request_type: type[
        garage_pb2.OpenGarageDoorRequest | garage_pb2.CloseGarageDoorRequest
    ],
    rpc: str,
) -> None:
    """The API sends the door's vendor id, the system and the token."""
    api = create_api()
    stub = MagicMock()
    setattr(stub, rpc, AsyncMock(return_value=MagicMock()))
    with (
        patch.object(api, "is_session_valid", return_value=True),
        patch("vivintpy.api.grpc.aio.secure_channel") as channel,
        patch("vivintpy.api.garage_pb2_grpc.GarageStub", return_value=stub),
    ):
        channel.return_value.__aenter__ = AsyncMock()
        channel.return_value.__aexit__ = AsyncMock(return_value=False)
        await getattr(api, method)(PANEL_ID, "myq-abc123")

    await_args = cast(AsyncMock, getattr(stub, rpc)).await_args
    assert await_args
    request = await_args.args[0]
    assert isinstance(request, request_type)
    assert request.vendor_device_id == "myq-abc123"
    assert await_args.kwargs["metadata"] == [
        ("authorization", "Bearer access"),
        ("x-viv-system-id", str(PANEL_ID)),
    ]


async def test_api_raises_status_code() -> None:
    """A failed call raises an error carrying the service's status code."""
    api = create_api()
    stub = MagicMock()
    stub.OpenGarageDoor = AsyncMock(
        side_effect=AioRpcError(grpc.StatusCode.UNIMPLEMENTED, "nope")
    )
    with (
        patch.object(api, "is_session_valid", return_value=True),
        patch("vivintpy.api.grpc.aio.secure_channel") as channel,
        patch("vivintpy.api.garage_pb2_grpc.GarageStub", return_value=stub),
        pytest.raises(VivintSkyGrpcError, match="OpenGarageDoor failed") as err,
    ):
        channel.return_value.__aenter__ = AsyncMock()
        channel.return_value.__aexit__ = AsyncMock(return_value=False)
        await api.open_garage_door(PANEL_ID, VENDOR_ID)
    assert err.value.code == grpc.StatusCode.UNIMPLEMENTED


def http_response(status: int, body: dict) -> MagicMock:
    """Return a JSON response with the status and body."""
    resp = MagicMock()
    resp.status = status
    resp.content_type = "application/json"
    resp.json = AsyncMock(return_value=body)
    resp.method = "PUT"
    resp.url.path = f"/api/{PANEL_ID}/{PARTITION_ID}/door/{DEVICE_ID}"
    resp.raise_for_status.side_effect = ClientResponseError(
        MagicMock(), (), status=status
    )
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


@pytest.mark.parametrize(
    ("status", "error"), [(500, ClientResponseError), (403, VivintSkyApiError)]
)
async def test_failed_request_logs_body(
    status: int, error: type[Exception], caplog: pytest.LogCaptureFixture
) -> None:
    """A failed request logs the server's response before raising."""
    api = create_api()
    session = api._VivintSkyApi__client_session  # type: ignore[attr-defined]
    session.closed = False
    session.put = AsyncMock(return_value=http_response(status, {"msg": "door busy"}))
    caplog.set_level(logging.DEBUG, logger="vivintpy.api")
    with (
        patch.object(api, "is_session_valid", return_value=True),
        pytest.raises(error),
    ):
        await api.set_garage_door_state(
            PANEL_ID, PARTITION_ID, DEVICE_ID, GarageDoorState.OPENING
        )
    assert f"failed with {status}: {{'msg': 'door busy'}}" in caplog.text


async def test_failed_sign_in_is_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    """A failed sign-in doesn't put the identity provider's response in the log."""
    api = create_api()
    session = api._VivintSkyApi__client_session  # type: ignore[attr-defined]
    session.closed = False
    session.post = AsyncMock(return_value=http_response(401, {"error": "denied"}))
    caplog.set_level(logging.DEBUG, logger="vivintpy.api")
    with pytest.raises(VivintSkyApiAuthenticationError):
        await api._VivintSkyApi__call(  # type: ignore[attr-defined]
            session.post, f"{AUTH_ENDPOINT}/oauth2/token"
        )
    assert "failed with" not in caplog.text

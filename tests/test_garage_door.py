"""Test the garage door."""

from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest

from vivintpy.api import VivintSkyApi, garage_vendor_device_id
from vivintpy.devices.garage_door import GarageDoor
from vivintpy.enums import GarageDoorState
from vivintpy.exceptions import VivintSkyGrpcError
from vivintpy.proto import garage_pb2
from vivintpy.system import System

PANEL_ID = 8070719956882364
PARTITION_ID = 1
DEVICE_ID = 45


def create_garage_door() -> tuple[GarageDoor, MagicMock]:
    """Return a garage door on a panel and the mocked API it uses."""
    api = MagicMock()
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


def test_vendor_device_id() -> None:
    """The garage service names a panel door by its panel and device id."""
    assert (
        garage_vendor_device_id(PANEL_ID, DEVICE_ID)
        == "urn:vivint:panel:8070719956882364:45"
    )


async def test_open_uses_garage_service() -> None:
    """Opening a door goes through the garage service, not the door endpoint."""
    door, api = create_garage_door()
    await door.open()
    api.open_garage_door.assert_awaited_once_with(PANEL_ID, DEVICE_ID)
    api.set_garage_door_state.assert_not_awaited()


async def test_close_uses_garage_service() -> None:
    """Closing a door goes through the garage service, not the door endpoint."""
    door, api = create_garage_door()
    await door.close()
    api.close_garage_door.assert_awaited_once_with(PANEL_ID, DEVICE_ID)
    api.set_garage_door_state.assert_not_awaited()


async def test_unimplemented_falls_back_to_door_endpoint() -> None:
    """A garage service without the method falls back to the door endpoint."""
    door, api = create_garage_door()
    api.open_garage_door.side_effect = grpc_error(grpc.StatusCode.UNIMPLEMENTED)
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
    api.open_garage_door.assert_not_awaited()
    api.close_garage_door.assert_not_awaited()
    api.set_garage_door_state.assert_awaited_once_with(
        PANEL_ID, PARTITION_ID, DEVICE_ID, GarageDoorState.STOPPED
    )


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
    """The API names the door by its vendor id and sends the system and token."""
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
        await getattr(api, method)(PANEL_ID, DEVICE_ID)

    await_args = cast(AsyncMock, getattr(stub, rpc)).await_args
    assert await_args
    request = await_args.args[0]
    assert isinstance(request, request_type)
    assert request.vendor_device_id == "urn:vivint:panel:8070719956882364:45"
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
        await api.open_garage_door(PANEL_ID, DEVICE_ID)
    assert err.value.code == grpc.StatusCode.UNIMPLEMENTED

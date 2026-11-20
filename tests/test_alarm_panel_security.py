"""Test arming and disarming an alarm panel through the security service."""

from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest

from vivintpy.api import VivintSkyApi
from vivintpy.devices.alarm_panel import AlarmPanel
from vivintpy.enums import ArmedState
from vivintpy.exceptions import VivintSkyApiError, VivintSkyGrpcError
from vivintpy.proto import security_pb2
from vivintpy.system import System

PANEL_ID = 1234567890123456
VENDOR_ID = f"urn:vivint:panel:{PANEL_ID}"


def create_alarm_panel(
    partition_id: int = 1, vendor_device_id: str = VENDOR_ID
) -> tuple[AlarmPanel, MagicMock]:
    """Return an alarm panel and the mocked API it uses.

    The security service returns `vendor_device_id` for the panel.
    """
    api = MagicMock()
    api.get_security_state = AsyncMock(
        return_value=security_pb2.GetSecurityStateResponse(
            vendor_device_id=vendor_device_id
        )
    )
    api.arm_security = AsyncMock()
    api.disarm_security = AsyncMock()
    api.set_alarm_state = AsyncMock()
    system = System(
        {
            "system": {
                "panid": PANEL_ID,
                "u": [],
                "par": [{"panid": PANEL_ID, "parid": partition_id, "s": 0, "d": []}],
            }
        },
        api,
        name="Home",
        is_admin=True,
    )
    return system.alarm_panels[0], api


def grpc_error(code: grpc.StatusCode) -> VivintSkyGrpcError:
    """Return the error the API raises when the security service fails."""
    return VivintSkyGrpcError("ArmSecurity", code, "rejected")


@pytest.mark.parametrize(
    ("method", "arm_state"),
    [
        ("arm_stay", security_pb2.ArmSecurityRequest.ARM_STATE_ARMED_STAY),
        ("arm_away", security_pb2.ArmSecurityRequest.ARM_STATE_ARMED_AWAY),
    ],
)
async def test_arm_uses_security_service(
    method: str, arm_state: security_pb2.ArmSecurityRequest.ArmState
) -> None:
    """Arming goes through the security service, not the armed states endpoint."""
    panel, api = create_alarm_panel()
    await getattr(panel, method)()
    api.get_security_state.assert_awaited_once_with(PANEL_ID)
    api.arm_security.assert_awaited_once_with(PANEL_ID, VENDOR_ID, arm_state)
    api.set_alarm_state.assert_not_awaited()


async def test_disarm_uses_security_service() -> None:
    """Disarming goes through the security service, not the armed states endpoint."""
    panel, api = create_alarm_panel()
    await panel.disarm()
    api.disarm_security.assert_awaited_once_with(PANEL_ID, VENDOR_ID)
    api.arm_security.assert_not_awaited()
    api.set_alarm_state.assert_not_awaited()


async def test_service_id_is_kept() -> None:
    """The panel's security service id is looked up once."""
    panel, api = create_alarm_panel()
    await panel.arm_away()
    await panel.disarm()
    api.get_security_state.assert_awaited_once_with(PANEL_ID)
    api.disarm_security.assert_awaited_once_with(PANEL_ID, VENDOR_ID)


@pytest.mark.parametrize("failing", ["get_security_state", "arm_security"])
async def test_unimplemented_falls_back_to_endpoint(failing: str) -> None:
    """A security service without the method falls back to the endpoint."""
    panel, api = create_alarm_panel()
    getattr(api, failing).side_effect = grpc_error(grpc.StatusCode.UNIMPLEMENTED)
    await panel.arm_away()
    api.set_alarm_state.assert_awaited_once_with(PANEL_ID, 1, ArmedState.ARMED_AWAY)


async def test_other_errors_do_not_fall_back() -> None:
    """A rejected command is raised instead of retried on the endpoint."""
    panel, api = create_alarm_panel()
    api.arm_security.side_effect = grpc_error(grpc.StatusCode.PERMISSION_DENIED)
    with pytest.raises(VivintSkyGrpcError, match="PERMISSION_DENIED"):
        await panel.arm_away()
    api.set_alarm_state.assert_not_awaited()


async def test_missing_service_id_is_not_sent() -> None:
    """A panel the security service returns no id for isn't armed by it."""
    panel, api = create_alarm_panel(vendor_device_id="")
    with pytest.raises(VivintSkyApiError, match="didn't return an id"):
        await panel.arm_away()
    api.arm_security.assert_not_awaited()
    api.set_alarm_state.assert_not_awaited()


async def test_other_partitions_use_endpoint() -> None:
    """The service arms a whole system, so another partition uses the endpoint."""
    panel, api = create_alarm_panel(partition_id=2)
    await panel.arm_stay()
    api.get_security_state.assert_not_awaited()
    api.set_alarm_state.assert_awaited_once_with(PANEL_ID, 2, ArmedState.ARMED_STAY)


async def test_other_states_use_endpoint() -> None:
    """States the security service can't set still go to the endpoint."""
    panel, api = create_alarm_panel()
    await panel.set_armed_state(ArmedState.WALK_TEST)
    api.get_security_state.assert_not_awaited()
    api.set_alarm_state.assert_awaited_once_with(PANEL_ID, 1, ArmedState.WALK_TEST)


def create_api() -> VivintSkyApi:
    """Return an API with a valid session."""
    api = VivintSkyApi("user", refresh_token="refresh", client_session=MagicMock())
    api._VivintSkyApi__token = {"access_token": "access"}  # type: ignore[attr-defined]
    return api


async def call_service(
    rpc: str, response: object, call: str, *args: object
) -> tuple[MagicMock, object]:
    """Call an API method with the security service answering `response`.

    Return the stub, so a test can check the request it got, and what the
    method returned.
    """
    api = create_api()
    stub = MagicMock()
    setattr(stub, rpc, AsyncMock(return_value=response))
    with (
        patch.object(api, "is_session_valid", return_value=True),
        patch("vivintpy.api.grpc.aio.secure_channel") as channel,
        patch("vivintpy.api.security_pb2_grpc.SecurityStub", return_value=stub),
    ):
        channel.return_value.__aenter__ = AsyncMock()
        channel.return_value.__aexit__ = AsyncMock(return_value=False)
        result = await getattr(api, call)(*args)
    return stub, result


def sent(stub: MagicMock, rpc: str) -> tuple[object, list]:
    """Return the request and metadata the stub's `rpc` was called with."""
    await_args = cast(AsyncMock, getattr(stub, rpc)).await_args
    assert await_args
    return await_args.args[0], await_args.kwargs["metadata"]


async def test_api_gets_security_state() -> None:
    """The API asks for the system's state with the system and the token."""
    response = security_pb2.GetSecurityStateResponse(vendor_device_id=VENDOR_ID)
    stub, result = await call_service(
        "GetSecurityState", response, "get_security_state", PANEL_ID
    )
    assert result == response
    request, metadata = sent(stub, "GetSecurityState")
    assert request == security_pb2.GetSecurityStateRequest(system_id=PANEL_ID)
    assert metadata == [
        ("authorization", "Bearer access"),
        ("x-viv-system-id", str(PANEL_ID)),
    ]


async def test_api_arms() -> None:
    """The API arms like the app: keeping the entry delay, without forcing it."""
    stub, _ = await call_service(
        "ArmSecurity",
        security_pb2.ArmSecurityResponse(result=True),
        "arm_security",
        PANEL_ID,
        VENDOR_ID,
        security_pb2.ArmSecurityRequest.ARM_STATE_ARMED_AWAY,
    )
    request, _ = sent(stub, "ArmSecurity")
    assert request == security_pb2.ArmSecurityRequest(
        vendor_device_id=VENDOR_ID,
        arm_state=security_pb2.ArmSecurityRequest.ARM_STATE_ARMED_AWAY,
        disable_entry_delay=False,
        force_arm=False,
    )


async def test_api_disarms() -> None:
    """The API disarms the panel by its security service id."""
    stub, _ = await call_service(
        "DisarmSecurity",
        security_pb2.DisarmSecurityResponse(result=True),
        "disarm_security",
        PANEL_ID,
        VENDOR_ID,
    )
    request, _ = sent(stub, "DisarmSecurity")
    assert request == security_pb2.DisarmSecurityRequest(vendor_device_id=VENDOR_ID)


@pytest.mark.parametrize(
    ("rpc", "response", "call", "args"),
    [
        (
            "ArmSecurity",
            security_pb2.ArmSecurityResponse(result=False),
            "arm_security",
            (PANEL_ID, VENDOR_ID, security_pb2.ArmSecurityRequest.ARM_STATE_ARMED_STAY),
        ),
        (
            "DisarmSecurity",
            security_pb2.DisarmSecurityResponse(result=False),
            "disarm_security",
            (PANEL_ID, VENDOR_ID),
        ),
    ],
)
async def test_api_raises_when_not_done(
    rpc: str, response: object, call: str, args: tuple
) -> None:
    """A security service that answers without arming or disarming raises."""
    with pytest.raises(VivintSkyApiError, match="didn't"):
        await call_service(rpc, response, call, *args)

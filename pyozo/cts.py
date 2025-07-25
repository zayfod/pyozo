"""

Control service (CTS) module.

"""

from typing import Tuple, Optional, cast
import logging

from .protocol_utils import BaseModel
from .cts_client import ControlServiceClient
from .cts_encoder import (
    raise_for_call_status,
    message_id,
    Lights,
    IntersectionDirection,
    LineNavigationAction,
    CalibrationType,
    FirmwareUpdateTarget,
    FirmwareUpdateSource,
    WatcherFlags,
    WatcherRegionFlags,
    PacketRequest_MoveStraight,
    PacketResponse_MoveStraight,
    PacketRequest_Rotate,
    PacketResponse_Rotate,
    PacketRequest_Velocity,
    PacketResponse_Velocity,
    PacketRequest_LineNavigation,
    PacketResponse_LineNavigation,
    PacketRequest_ExecuteFile,
    PacketResponse_ExecuteFile,
    PacketRequest_SetLED,
    PacketResponse_SetLED,
    PacketRequest_Calibrate,
    PacketResponse_Calibrate,
    PacketRequest_TurnOff,
    PacketResponse_TurnOff,
    PacketRequest_PlayTone,
    PacketResponse_PlayTone,
    PacketRequest_StopExecution,
    PacketResponse_StopExecution,
    PacketRequest_WatcherSetup,
    PacketResponse_WatcherSetup,
    PacketRequest_WatcherRegionSetup,
    PacketResponse_WatcherRegionSetup,
    ExecutionState,
    PacketEvent_PreciseMovementExecutionUpdate,
    PacketEvent_VelocityExecutionState,
    PacketEvent_LineNavigationExecutionUpdate,
    PacketEvent_AudioExecutionState,
)


__all__ = [
    "ControlService",
]


logger = logging.getLogger("pyozo.cts")


def raise_for_request_id(request_id: int, expected_request_id: int) -> None:
    if request_id != expected_request_id:
        raise RuntimeError(f"Response with request ID {request_id} while expecting {expected_request_id}.")


class ControlService:
    def __init__(self, client: ControlServiceClient) -> None:
        self.client = client
        self.request_id = 100

    def _get_next_request_id(self) -> int:
        request_id = self.request_id
        self.request_id += 1
        return request_id

    async def _wait_execution(self, event_id: int, request_id: int, timeout: Optional[float] = None) -> BaseModel:
        while True:
            event = await self.client.wait_for_event(event_id, request_id, timeout=timeout)
            execution_state = event.execution_state if hasattr(event, "execution_state") else None
            if execution_state in (ExecutionState.FINISHED_NORMAL, ExecutionState.FINISHED_FORCED):
                return event

    async def mem_read(self, address: int, length: int) -> bytes:
        return await self.client.mem_read(address=int(address), length=int(length))

    async def mem_write(self, address: int, data: bytes) -> None:
        await self.client.mem_write(int(address), data)

    async def move_straight(self, distance_m: float, speed_mps: float) -> PacketEvent_PreciseMovementExecutionUpdate:
        request = PacketRequest_MoveStraight(
            distance_m=float(distance_m), speed_mps=float(speed_mps), request_id=self._get_next_request_id()
        )
        response = await self.client.request(request, message_id(PacketResponse_MoveStraight), request.request_id)
        response = cast(PacketResponse_MoveStraight, response)
        raise_for_request_id(response.request_id, request.request_id)
        event = await self._wait_execution(message_id(PacketEvent_PreciseMovementExecutionUpdate), request.request_id)
        event = cast(PacketEvent_PreciseMovementExecutionUpdate, event)
        return event

    async def rotate(self, angle_rad: float, speed_radps: float) -> PacketEvent_PreciseMovementExecutionUpdate:
        request = PacketRequest_Rotate(
            angle_rad=float(angle_rad), speed_radps=float(speed_radps), request_id=self._get_next_request_id()
        )
        response = await self.client.request(request, message_id(PacketResponse_Rotate), request.request_id)
        response = cast(PacketResponse_Rotate, response)
        raise_for_request_id(response.request_id, request.request_id)
        event = await self._wait_execution(message_id(PacketEvent_PreciseMovementExecutionUpdate), request.request_id)
        event = cast(PacketEvent_PreciseMovementExecutionUpdate, event)
        return event

    async def velocity(
        self, linear_speed_mps: float, angular_speed_radps: float, duration_ms: int = -1
    ) -> Optional[PacketEvent_VelocityExecutionState]:
        request = PacketRequest_Velocity(
            linear_speed_mps=float(linear_speed_mps),
            angular_speed_radps=float(angular_speed_radps),
            duration_ms=int(duration_ms),
            request_id=self._get_next_request_id(),
        )
        response = await self.client.request(request, message_id(PacketResponse_Velocity), request.request_id)
        response = cast(PacketResponse_Velocity, response)
        raise_for_request_id(response.request_id, request.request_id)
        if duration_ms:
            event = await self._wait_execution(message_id(PacketEvent_VelocityExecutionState), request.request_id)
            event = cast(PacketEvent_VelocityExecutionState, event)
            return event
        return None

    async def line_navigation(
        self, direction: IntersectionDirection, action: LineNavigationAction
    ) -> IntersectionDirection:
        request = PacketRequest_LineNavigation(
            direction=direction, action=action, request_id=self._get_next_request_id()
        )
        response = await self.client.request(request, message_id(PacketResponse_LineNavigation), request.request_id)
        response = cast(PacketResponse_LineNavigation, response)
        raise_for_request_id(response.request_id, request.request_id)
        event = await self._wait_execution(message_id(PacketEvent_LineNavigationExecutionUpdate), request.request_id)
        event = cast(PacketEvent_LineNavigationExecutionUpdate, event)
        return event.intersection_direction

    async def execute_file(self, path: str) -> None:
        request = PacketRequest_ExecuteFile(path=str(path), request_id=self._get_next_request_id())
        response = await self.client.request(request, message_id(PacketResponse_ExecuteFile), request.request_id)
        response = cast(PacketResponse_ExecuteFile, response)
        raise_for_request_id(response.request_id, request.request_id)
        await self._wait_execution(message_id(PacketEvent_AudioExecutionState), request.request_id)

    async def set_led(self, led_mask: Lights, red: int = 0, green: int = 0, blue: int = 0, alpha: int = 0) -> None:
        request = PacketRequest_SetLED(led_mask=led_mask, red=red, green=green, blue=blue, alpha=alpha)
        response = await self.client.request(request, message_id(PacketResponse_SetLED))
        response = cast(PacketResponse_SetLED, response)
        raise_for_call_status(response.call_status)

    async def calibrate(self, type: CalibrationType) -> None:
        request = PacketRequest_Calibrate(type=type)
        response = await self.client.request(request, message_id(PacketResponse_Calibrate))
        response = cast(PacketResponse_Calibrate, response)
        raise_for_call_status(response.call_status)

    async def turn_off(self) -> None:
        request = PacketRequest_TurnOff()
        # The respons never comes as the bot is turned off immediately.
        await self.client.request(request, message_id(PacketResponse_TurnOff), timeout=-1.0)
        # raise_for_call_status(response.call_status)

    async def update_firmware(self, target: FirmwareUpdateTarget, source: FirmwareUpdateSource) -> None:
        raise NotImplementedError()

    async def play_tone(self, frequency_hz: int, duration_ms: int, volume: int = 1) -> None:
        request = PacketRequest_PlayTone(
            frequency_hz=int(frequency_hz),
            duration_ms=int(duration_ms),
            volume=int(volume),
            request_id=self._get_next_request_id(),
        )
        response = await self.client.request(request, message_id(PacketResponse_PlayTone), request.request_id)
        response = cast(PacketResponse_PlayTone, response)
        raise_for_request_id(response.request_id, request.request_id)
        await self._wait_execution(message_id(PacketEvent_AudioExecutionState), request.request_id)

    async def stop_execution(self) -> None:
        request = PacketRequest_StopExecution(request_id=self._get_next_request_id())
        response = await self.client.request(request, message_id(PacketResponse_StopExecution), request.request_id)
        response = cast(PacketResponse_StopExecution, response)
        raise_for_request_id(response.request_id, request.request_id)

    async def watcher_setup(
        self, watcher_id: int, flags: WatcherFlags, notification_period_min_ms: int, notification_period_max_ms: int
    ) -> None:
        request = PacketRequest_WatcherSetup(
            watcher_id=int(watcher_id),
            flags=flags,
            notification_period_min_ms=int(notification_period_min_ms),
            notification_period_max_ms=int(notification_period_max_ms),
        )
        response = await self.client.request(request, message_id(PacketResponse_WatcherSetup))
        response = cast(PacketResponse_WatcherSetup, response)
        raise_for_call_status(response.call_status)

    async def watcher_region_setup(
        self,
        watcher_id: int,
        region_id: int,
        address: int,
        size: int,
        flags: WatcherRegionFlags = WatcherRegionFlags(0),
    ) -> None:
        request = PacketRequest_WatcherRegionSetup(
            watcher_id=int(watcher_id), region_id=int(region_id), address=int(address), size=int(size), flags=flags
        )
        response = await self.client.request(request, message_id(PacketResponse_WatcherRegionSetup))
        response = cast(PacketResponse_WatcherRegionSetup, response)
        raise_for_call_status(response.call_status)

    async def long_rpc_extesion_execute(self, data_length: int, data_crc: int) -> Tuple[int, int]:
        return await self.client.long_rpc_execute(data_length=int(data_length), data_crc=int(data_crc))

    async def set_rng_seed(self) -> None:
        raise NotImplementedError()

    async def sensors_logging(self) -> None:
        raise NotImplementedError()

    async def memory_test(self) -> None:
        raise NotImplementedError()

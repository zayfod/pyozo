"""

Robot representation module.

"""

from types import TracebackType
from typing import Optional, Callable, Awaitable, Self, cast, TypeAlias
from dataclasses import dataclass
import math
from uuid import UUID
import struct
import logging

from bleak import BleakClient
import packaging.version

from .cts_client import ControlServiceClient
from .cts import ControlService
from .cts_encoder import (
    ExecutionState,
    IntersectionDirection,
    PacketEvent_LineNavigationExecutionUpdate,
    PacketEvent_PreciseMovementExecutionUpdate,
)
from .fts_client import FileTransferServiceClient
from .fts import FileTransferService
from .protocol_utils import BaseModel, s24_to_float, float_to_s24
from .virtual_memory import (
    PROCESSED_COLOR_ADDRESS,
    PROCESSED_COLOR_SIZE,
    ProcessedColor,
    IR_PROXIMITY_ADDRESS,
    IR_PROXIMITY_SIZE,
    IRPoximity,
    RELATIVE_POSITION_ADDRESS,
    RELATIVE_POSITION_SIZE,
    RelativePosition,
    DEVICE_NAME_ADDRESS,
    DEVICE_NAME_SIZE,
    LINE_NAVIGATION_SPEED_ADDRESS,
    LINE_NAVIGATION_SPEED_SIZE,
    FW_VERSION_ADDRESS,
    FW_VERSION_SIZE,
    Version,
    SERIAL_NUMBER_ADDRESS,
    SERIAL_NUMBER_SIZE,
    BLUETOOTH_VERSION_ADDRESS,
    BLUETOOTH_VERSION_SIZE,
    BLUETOOTH_ADDRESS_ADDRESS,
    BLUETOOTH_ADDRESS_SIZE,
    WATCHERS_INFO_ADDRESS,
    WATCHERS_INFO_SIZE,
    WatchersInfo,
)

__all__ = [
    "LineNavigationUpdateHandler",
    "RobotGeometry",
    "Robot",
]


logger = logging.getLogger("pyozo.robot")


LineNavigationUpdateHandler: TypeAlias = Callable[
    ["Robot", int, ExecutionState, IntersectionDirection], Awaitable[None]
]


@dataclass(frozen=True)
class RobotGeometry:
    """Robot geometry constants."""

    ticks_per_meter: float
    """Number of wheel encoder ticks per meter."""
    ticks_per_wheel_revolution: int
    """Number of wheel encoder ticks per revolution."""
    wheel_track: float
    """Distance between the centers of the left and right wheels in meters."""
    wheel_diameter: float
    """Diameter of the wheels in meters."""
    max_speed_limit: float
    """Maximum speed limit in meters per second."""


class Robot:
    """Robot representation class."""

    def __init__(self, client: BleakClient) -> None:
        """Constructor."""
        self.client = client
        """Bleak client instance."""
        self.uuid = client.address
        """Bluetooth UUID as obtained from BleakClient."""
        self.cts_client = ControlServiceClient(client)
        """Control service client instance."""
        self.cts = ControlService(self.cts_client)
        """Control service instance."""
        self.fts_client = FileTransferServiceClient(client)
        """File transfer service client instance."""
        self.fts = FileTransferService(self.fts_client)
        """File transfer service instance."""
        self.geometry = RobotGeometry(
            ticks_per_meter=18851,
            ticks_per_wheel_revolution=700,
            wheel_track=0.023,
            wheel_diameter=0.01182,
            max_speed_limit=0.3,
        )
        """Robot geometry constants."""
        self.line_navigation_update_handler: Optional[LineNavigationUpdateHandler] = None

    async def connect(self) -> None:
        """Connect to the robot."""
        self.cts_client.event_handler = self._event_handler
        await self.cts_client.connect()
        await self.fts_client.connect()

    async def disconnect(self) -> None:
        """Disconnect from the robot."""
        await self.fts_client.disconnect()
        await self.cts_client.disconnect()

    async def __aenter__(self) -> Self:
        """Connect to the robot as part of entering a context."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Disconnect from the robot as part of leaving a context."""
        await self.disconnect()

    async def _event_handler(self, packet: BaseModel) -> None:
        """Handle events from the control service."""
        if isinstance(packet, PacketEvent_LineNavigationExecutionUpdate):
            if self.line_navigation_update_handler is not None:
                await self.line_navigation_update_handler(
                    self, packet.request_id, packet.execution_state, packet.intersection_direction
                )

    async def get_processed_color(self) -> ProcessedColor:
        """Get processed color sensor readings."""
        data = await self.cts.mem_read(PROCESSED_COLOR_ADDRESS, PROCESSED_COLOR_SIZE)
        value = cast(ProcessedColor, ProcessedColor.from_bytes(data))
        return value

    async def get_ir_proximity(self) -> IRPoximity:
        """Get IR proximity sensor readings."""
        data = await self.cts.mem_read(IR_PROXIMITY_ADDRESS, IR_PROXIMITY_SIZE)
        value = cast(IRPoximity, IRPoximity.from_bytes(data))
        return value

    async def get_relative_position(self) -> RelativePosition:
        """Get relative position and orientation from odometry."""
        data = await self.cts.mem_read(RELATIVE_POSITION_ADDRESS, RELATIVE_POSITION_SIZE)
        value = cast(RelativePosition, RelativePosition.from_bytes(data))
        return value

    async def get_name(self) -> str:
        """Get robot name from VM."""
        data = await self.cts.mem_read(DEVICE_NAME_ADDRESS, DEVICE_NAME_SIZE)
        name = data.decode("utf-8").rstrip("\0")
        return name

    async def get_fw_version(self) -> packaging.version.Version:
        """Get firmware version from VM."""
        data = await self.cts.mem_read(FW_VERSION_ADDRESS, FW_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        version = packaging.version.Version(f"{value.major}.{value.minor}.{value.patch}")
        return version

    async def get_line_navigation_speed(self) -> float:
        """Get line navigation speed in meters per second."""
        data = await self.cts.mem_read(LINE_NAVIGATION_SPEED_ADDRESS, LINE_NAVIGATION_SPEED_SIZE)
        speed_mps = s24_to_float(struct.unpack("<l", data)[0])
        return speed_mps

    async def set_line_navigation_speed(self, speed_mps: float) -> None:
        """Set line navigation speed in meters per second."""
        s24 = float_to_s24(float(speed_mps))
        data = struct.pack("<l", s24)
        await self.cts.mem_write(LINE_NAVIGATION_SPEED_ADDRESS, data)

    async def get_serial_number(self) -> UUID:
        """Get serial number from VM."""
        data = await self.cts.mem_read(SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_SIZE)
        serial = UUID(bytes=data)
        return serial

    async def get_bluetooth_version(self) -> packaging.version.Version:
        """Get Bluetooth module firmware version from VM."""
        data = await self.cts.mem_read(BLUETOOTH_VERSION_ADDRESS, BLUETOOTH_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        version = packaging.version.Version(f"{value.major}.{value.minor}.{value.patch}")
        return version

    async def get_bluetooth_address(self) -> str:
        """Get Bluetooth address from VM."""
        data = await self.cts.mem_read(BLUETOOTH_ADDRESS_ADDRESS, BLUETOOTH_ADDRESS_SIZE)
        return data.hex()

    async def get_watchers_info(self) -> WatchersInfo:
        """Get watcher information from VM."""
        data = await self.cts.mem_read(WATCHERS_INFO_ADDRESS, WATCHERS_INFO_SIZE)
        info = cast(WatchersInfo, WatchersInfo.from_bytes(data))
        return info

    async def get_assets_hash(self) -> str:
        """Get assets SHA256 checksum from file-system."""
        data = await self.fts.download_file("/system/config/assets.cnf")
        return data.decode("utf-8")

    async def move_wheels(self, left_mps: float, right_mps: float, duration_ms: int = -1) -> None:
        """Set the speed of the left and right wheels in meters per second."""
        linear_speed_mps = (right_mps + left_mps) / 2.0
        angular_speed_radps = (right_mps - left_mps) / self.geometry.wheel_track
        await self.cts.velocity(
            linear_speed_mps=linear_speed_mps, angular_speed_radps=angular_speed_radps, duration_ms=int(duration_ms)
        )

    async def rotate_deg(self, angle_deg: float, speed_degps: float) -> PacketEvent_PreciseMovementExecutionUpdate:
        """Rotate the robot by specifying angle in degrees and angular speed in degrees per second."""
        return await self.cts.rotate(math.radians(angle_deg), speed_radps=math.radians(speed_degps))

    async def set_line_navigation_update_handler(self, handler: Optional[LineNavigationUpdateHandler]) -> None:
        """Set a handler for line navigation updates."""
        self.line_navigation_update_handler = handler

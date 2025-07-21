"""

Robot representation module.

"""

from types import TracebackType
from typing import Optional, Self, cast
from dataclasses import dataclass
import math
from uuid import UUID

from bleak import BleakClient

from .cts_client import ControlServiceClient
from .cts import ControlService
from .fts_client import FileTransferServiceClient
from .fts import FileTransferService
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
    FW_VERSION_ADDRESS,
    FW_VERSION_SIZE,
    Version,
    SERIAL_NUMBER_ADDRESS,
    SERIAL_NUMBER_SIZE,
    BLUETOOTH_VERSION_ADDRESS,
    BLUETOOTH_VERSION_SIZE,
    BLUETOOTH_ADDRESS_ADDRESS,
    BLUETOOTH_ADDRESS_SIZE,
)

__all__ = [
    "RobotGeometry",
    "Robot",
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

    async def connect(self) -> None:
        """Connect to the robot."""
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

    async def get_fw_version(self) -> Version:
        """Get firmware version from VM."""
        data = await self.cts.mem_read(FW_VERSION_ADDRESS, FW_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        return value

    async def get_serial_number(self) -> UUID:
        """Get serial number from VM."""
        data = await self.cts.mem_read(SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_SIZE)
        serial = UUID(bytes=data)
        return serial

    async def get_bluetooth_version(self) -> Version:
        """Get Bluetooth module firmware version from VM."""
        data = await self.cts.mem_read(BLUETOOTH_VERSION_ADDRESS, BLUETOOTH_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        return value

    async def get_bluetooth_address(self) -> str:
        """Get Bluetooth address from VM."""
        data = await self.cts.mem_read(BLUETOOTH_ADDRESS_ADDRESS, BLUETOOTH_ADDRESS_SIZE)
        return data.hex()

    async def get_assets_hash(self) -> str:
        """Get assets SHA256 checksum from file-system."""
        data = await self.fts.download_file("/system/config/assets.cnf")
        return data.decode("utf-8")

    async def move_wheels(self, left_mps: float, right_mps: float, duration_ms: int = -1) -> int:
        """Set the speed of the left and right wheels in meters per second."""
        linear_speed_mps = (right_mps + left_mps) / 2.0
        angular_speed_radps = (right_mps - left_mps) / self.geometry.wheel_track
        request_id = await self.cts.velocity(
            linear_speed_mps=linear_speed_mps, angular_speed_radps=angular_speed_radps, duration_ms=int(duration_ms)
        )
        return request_id

    async def rotate_deg(self, angle_deg: float, speed_degps: float) -> int:
        """Rotate the robot by specifying angle in degrees and angular speed in degrees per second."""
        return await self.cts.rotate(math.radians(angle_deg), speed_radps=math.radians(speed_degps))

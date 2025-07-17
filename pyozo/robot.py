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
    ticks_per_meter: float
    wheel_track: float
    wheel_diameter: float
    encoder_ticks_per_wheel_revolution: int
    max_speed_limit: float


class Robot:
    GEOMETRY = RobotGeometry(
        ticks_per_meter=18851,
        wheel_track=0.023,
        wheel_diameter=0.01182,
        encoder_ticks_per_wheel_revolution=700,
        max_speed_limit=0.3,
    )

    def __init__(self, client: BleakClient) -> None:
        self.client = client
        self.uuid = client.address
        self.cts_client = ControlServiceClient(client)
        self.cts = ControlService(self.cts_client)
        self.fts_client = FileTransferServiceClient(client)
        self.fts = FileTransferService(self.fts_client)

    async def connect(self) -> None:
        await self.cts_client.connect()
        await self.fts_client.connect()

    async def disconnect(self) -> None:
        await self.fts_client.disconnect()
        await self.cts_client.disconnect()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.disconnect()

    async def get_processed_color(self) -> ProcessedColor:
        data = await self.cts.mem_read(PROCESSED_COLOR_ADDRESS, PROCESSED_COLOR_SIZE)
        value = cast(ProcessedColor, ProcessedColor.from_bytes(data))
        return value

    async def get_ir_proximity(self) -> IRPoximity:
        data = await self.cts.mem_read(IR_PROXIMITY_ADDRESS, IR_PROXIMITY_SIZE)
        value = cast(IRPoximity, IRPoximity.from_bytes(data))
        return value

    async def get_relative_position(self) -> RelativePosition:
        data = await self.cts.mem_read(RELATIVE_POSITION_ADDRESS, RELATIVE_POSITION_SIZE)
        value = cast(RelativePosition, RelativePosition.from_bytes(data))
        return value

    async def get_name(self) -> str:
        data = await self.cts.mem_read(DEVICE_NAME_ADDRESS, DEVICE_NAME_SIZE)
        name = data.decode("utf-8").rstrip("\0")
        return name

    async def get_fw_version(self) -> Version:
        data = await self.cts.mem_read(FW_VERSION_ADDRESS, FW_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        return value

    async def get_serial_number(self) -> UUID:
        data = await self.cts.mem_read(SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_SIZE)
        serial = UUID(bytes=data)
        return serial

    async def get_bluetooth_version(self) -> Version:
        data = await self.cts.mem_read(BLUETOOTH_VERSION_ADDRESS, BLUETOOTH_VERSION_SIZE)
        value = cast(Version, Version.from_bytes(data))
        return value

    async def get_bluetooth_address(self) -> str:
        data = await self.cts.mem_read(BLUETOOTH_ADDRESS_ADDRESS, BLUETOOTH_ADDRESS_SIZE)
        return data.hex()

    async def get_assets_hash(self) -> str:
        data = await self.fts.download_file("/system/config/assets.cnf")
        return data.decode("utf-8")

    async def move_wheels(self, left_mps: float, right_mps: float, duration_ms: int = -1) -> int:
        linear_speed_mps = (right_mps + left_mps) / 2.0
        angular_speed_radps = (right_mps - left_mps) / self.GEOMETRY.wheel_track
        request_id = await self.cts.velocity(
            linear_speed_mps=linear_speed_mps, angular_speed_radps=angular_speed_radps, duration_ms=int(duration_ms)
        )
        return request_id

    async def rotate_deg(self, angle_deg: float, speed_degps: float) -> int:
        return await self.cts.rotate(math.radians(angle_deg), speed_radps=math.radians(speed_degps))

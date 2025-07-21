"""

Virtual memory data structure definitions.

"""

from .protocol_utils import BaseModel, Field, FieldType


__all__ = [
    "PROCESSED_COLOR_ADDRESS",
    "PROCESSED_COLOR_SIZE",
    "IR_PROXIMITY_ADDRESS",
    "IR_PROXIMITY_SIZE",
    "RELATIVE_POSITION_ADDRESS",
    "RELATIVE_POSITION_SIZE",
    "DEVICE_NAME_ADDRESS",
    "DEVICE_NAME_SIZE",
    "LONG_RPC_EXTENSION_DATA_ADDRESS",
    "LONG_RPC_EXTENSION_DATA_SIZE",
    "FW_VERSION_ADDRESS",
    "FW_VERSION_SIZE",
    "BLUETOOTH_VERSION_ADDRESS",
    "BLUETOOTH_VERSION_SIZE",
    "BLUETOOTH_ADDRESS_ADDRESS",
    "BLUETOOTH_ADDRESS_SIZE",
    "ProcessedColor",
    "IRPoximity",
    "RelativePosition",
    "Version",
]


PROCESSED_COLOR_ADDRESS = 0x000045
PROCESSED_COLOR_SIZE = 11
IR_PROXIMITY_ADDRESS = 0x000076
IR_PROXIMITY_SIZE = 8
RELATIVE_POSITION_ADDRESS = 0x0000A2
RELATIVE_POSITION_SIZE = 21
DEVICE_NAME_ADDRESS = 0x004000
DEVICE_NAME_SIZE = 17
LONG_RPC_EXTENSION_DATA_ADDRESS = 0x006000
LONG_RPC_EXTENSION_DATA_SIZE = 128
FW_VERSION_ADDRESS = 0x1002C
FW_VERSION_SIZE = 4
SERIAL_NUMBER_ADDRESS = 0x10050
SERIAL_NUMBER_SIZE = 16
BLUETOOTH_VERSION_ADDRESS = 0x10060
BLUETOOTH_VERSION_SIZE = 4
BLUETOOTH_ADDRESS_ADDRESS = 0x10065
BLUETOOTH_ADDRESS_SIZE = 6


class ProcessedColor(BaseModel):
    """Processed color sensor readings."""

    # Normalized values.
    red: int = Field(FieldType.UINT8, default=0)
    green: int = Field(FieldType.UINT8, default=0)
    blue: int = Field(FieldType.UINT8, default=0)
    transformed_red: int = Field(FieldType.UINT8, default=0)
    transformed_green: int = Field(FieldType.UINT8, default=0)
    transformed_blue: int = Field(FieldType.UINT8, default=0)
    light_source: int = Field(FieldType.UINT8, default=0)
    timestamp: int = Field(FieldType.INT32, default=0)


class IRPoximity(BaseModel):
    """Infrared proximity sensor readings."""

    left_rear: int = Field(FieldType.UINT8, default=0)
    left_front: int = Field(FieldType.UINT8, default=0)
    right_rear: int = Field(FieldType.UINT8, default=0)
    right_front: int = Field(FieldType.UINT8, default=0)
    timestamp: int = Field(FieldType.INT32, default=0)


class RelativePosition(BaseModel):
    """Relative robot position and orientation, obtained from odometry."""

    counter: int = Field(FieldType.UINT8, default=0)
    x: float = Field(FieldType.FLOAT, default=0.0)
    y: float = Field(FieldType.FLOAT, default=0.0)
    angle_x: float = Field(FieldType.FLOAT, default=0.0)
    angle_y: float = Field(FieldType.FLOAT, default=0.0)
    timestamp: int = Field(FieldType.INT32, default=0)


class Version(BaseModel):
    """Software version."""

    major: int = Field(FieldType.UINT8, default=0)
    minor: int = Field(FieldType.UINT8, default=0)
    patch: int = Field(FieldType.UINT16, default=0)

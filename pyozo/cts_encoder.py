"""

Control service protocol encoder module.

"""

from enum import Enum, Flag
import struct

from .protocol_utils import FieldType, Field, BaseModel


__all__ = [
    "CTRL_SERVICE",
    "CTRL_CHARACTERISTIC",
    "MAX_PACKET_SIZE",
    "IOResult",
    "IntersectionDirection",
    "LineNavigationAction",
    "Lights",
    "CallStatus",
    "CalibrationType",
    "FirmwareUpdateTarget",
    "FirmwareUpdateSource",
    "WatcherFlags",
    "WatcherRegionFlags",
    "LoggingState",
    "MemoryTestType",
    "ExecutionState",
    "ShutdownSource",
    "CalibrationResult",
    "MemoryTestFields",
    "ErrorModuleID",
    "PacketRequest_MemRead",
    "PacketResponse_MemRead",
    "PacketRequest_MemWrite",
    "PacketResponse_MemWrite",
    "PacketRequest_MoveStraight",
    "PacketResponse_MoveStraight",
    "PacketRequest_Rotate",
    "PacketResponse_Rotate",
    "PacketRequest_Velocity",
    "PacketResponse_Velocity",
    "PacketRequest_LineNavigation",
    "PacketResponse_LineNavigation",
    "PacketRequest_ExecuteFile",
    "PacketResponse_ExecuteFile",
    "PacketRequest_SetLED",
    "PacketResponse_SetLED",
    "PacketRequest_Calibrate",
    "PacketResponse_Calibrate",
    "PacketRequest_TurnOff",
    "PacketResponse_TurnOff",
    "PacketRequest_UpdateFirmware",
    "PacketResponse_UpdateFirmware",
    "PacketRequest_PlayTone",
    "PacketResponse_PlayTone",
    "PacketRequest_StopExecution",
    "PacketResponse_StopExecution",
    "PacketRequest_WatcherSetup",
    "PacketResponse_WatcherSetup",
    "PacketRequest_WatcherRegionSetup",
    "PacketResponse_WatcherRegionSetup",
    "PacketRequest_LongRPCExtensionExecute",
    "PacketResponse_LongRPCExtensionExecute",
    "PacketRequest_SetRNGSeed",
    "PacketResponse_SetRNGSeed",
    "PacketRequest_SensorsLogging",
    "PacketResponse_SensorsLogging",
    "PacketRequest_MemoryTest",
    "PacketResponse_MemoryTest",
    "PacketEvent_PreciseMovementExecutionUpdate",
    "PacketEvent_LineNavigationExecutionUpdate",
    "PacketEvent_Shutdown",
    "PacketEvent_AudioExecutionState",
    "PacketEvent_WatcherDirty",
    "PacketEvent_CalibrationStatus",
    "PacketEvent_MemoryTestStatus",
    "PacketEvent_ModuleError",
    "PacketEvent_VirtualMachineExecutionState",
    "PacketEvent_VelocityExecutionState",
    "packet_from_bytes",
    "raise_for_ioresult",
    "raise_for_call_status",
    "message_id",
]


CTRL_SERVICE = "8903136c-5f13-4548-a885-c58779136801"
"""Control Bluetooth service UUID."""
CTRL_CHARACTERISTIC = "8903136c-5f13-4548-a885-c58779136802"
"""Control Bluetooth characteristic UUID."""
MAX_PACKET_SIZE = 20
"""Maximum packet size in bytes, bound by Bluetooth MTU."""


class IOResult(Enum):
    SUCCESS = 0
    ERROR_UNKNOWN = 1
    ERROR_READONLY = 2
    ERROR_PERMISSION_DENIED = 3
    ERROR_OUT_OF_RANGE = 4
    ERROR_RANGE_TOO_LARGE = 5
    ERROR_MISALIGNED = 6
    ERROR_PARTIAL_WRITE = 7
    ERROR_INVALID_DATA = 8


class IntersectionDirection(Flag):
    LEFT = 0x01
    STRAIGHT = 0x02
    RIGHT = 0x04
    BACKWARD = 0x08


class LineNavigationAction(Enum):
    DO_NOT_FOLLOW = 0
    FOLLOW = 1


class Lights(Flag):
    TOP = 0x01
    FRONT_LEFT = 0x02
    FRONT_1 = 0x02
    FRONT_LEFT_CENTER = 0x04
    FRONT_2 = 0x04
    FRONT_CENTER = 0x08
    FRONT_3 = 0x08
    FRONT_RIGHT_CENTER = 0x10
    FRONT_4 = 0x10
    FRONT_RIGHT = 0x20
    FRONT_5 = 0x20
    BUTTON = 0x40
    BACK = 0x80
    ALL_FRONT = 0x3E
    ALL_ROBOT = 0xFF


class CallStatus(Enum):
    SUCCESS = 0
    INVALID_PARAMETERS = 1
    ERROR = 2
    UNSUPPORTED = 3


class CalibrationType(Enum):
    ENCODERS = 0
    LINE_SENSORS = 1
    COLOR_SENSOR = 2
    HEIGHT_SENSOR = 3
    ON_SPOT = 4
    ON_SPOT_WITHOUT_ENCODERS = 5


class FirmwareUpdateTarget(Enum):
    MAIN_MCU = 0
    WIRELESS_MCU = 1


class FirmwareUpdateSource(Enum):
    FILE_SYSTEM = 0
    RECOVERY = 1


class WatcherFlags(Flag):
    ENABLED = 0x01
    DISABLE_WHEN_DISCONNECTED = 0x02
    SEND_INITIAL_VALUE = 0x04


class WatcherRegionFlags(Flag):
    DO_NOT_SET_DIRTY = 0x01
    DO_NOT_SEND_IN_NOTIFY = 0x02


class LoggingState(Enum):
    OFF = 0
    ON_STOP_WITH_SAMPLE_DROP = 1
    ON_IGNORE_SAMPLE_DROP = 2


class MemoryTestType(Enum):
    FULL_TEST_REPORT = 0
    FULL_TEST = 1
    QUICK_TEST = 2


class ExecutionState(Enum):
    RUNNING = 0
    FINISHED_NORMAL = 1
    FINISHED_FORCED = 2
    NOT_EXECUTED = 3
    FILE_NOT_FOUND = 4
    INVALID_REQUEST = 5
    CORRUPTED_INPUT = 6


class ShutdownSource(Enum):
    BUTTON = 0
    LOW_BATTERY = 1
    SYSTEM_API = 2
    RESTART = 3
    CHARGER_DISCONNECT = 4
    BLE_DISCONNECT = 5
    COLOR_CODE = 6
    OZO_VM = 7


class CalibrationResult(Enum):
    SUCCESS = 0
    ENCODERS_FAILURE = 1
    LINE_SENSORS_THRESHOLD_FAILURE = 2
    COLOR_SENSOR_THRESHOLD_FAILURE = 3
    LINE_SENSORS_CALIBRATION_ALIGNMENT_FAILURE = 4
    COLOR_SENSOR_CALIBRATION_ALIGNMENT_FAILURE = 5
    NEW_DOT_LINE_ALIGNMENT_FAILURE = 6
    NEW_DOT_FINAL_ALIGNMENT_FAILURE = 7


class MemoryTestFields(Flag):
    PAGE_ERROR = 0x01


class ErrorModuleID(Enum):
    OZO_VM_PROGRAM_STREAM_LOADER = 0
    OZO_VM_LOAD_FROM_COLORS = 1
    OZO_VM_SYSTEM_CALLS = 2
    BLUETOOTH = 4
    UNSUPPORTED_OPERATION = 5
    VIRTUAL_MACHINE_TASK = 7
    BRIGHTNESS_CONTROL = 8
    CONTROL_PROTOCOL = 9
    UNDEFINED = 255


class PacketRequest_MemRead(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=1)
    address: int = Field(FieldType.UINT32, default=0)
    length: int = Field(FieldType.UINT16, default=0)


class PacketResponse_MemRead(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=2)
    result: IOResult = Field(FieldType.UINT8, default=IOResult.SUCCESS)
    length: int = Field(FieldType.UINT16, default=0)
    data: bytes = Field(FieldType.BYTES, default=b"")


class PacketRequest_MemWrite(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=3)
    address: int = Field(FieldType.UINT32, default=0)
    length: int = Field(FieldType.UINT16, default=0)
    data: bytes = Field(FieldType.BYTES, default=b"")


class PacketResponse_MemWrite(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=4)
    result: IOResult = Field(FieldType.UINT8, default=IOResult.SUCCESS)


class PacketRequest_MoveStraight(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=100)
    request_id: int = Field(FieldType.UINT32, default=0)
    distance_m: float = Field(FieldType.FLOAT, default=0.0)
    speed_mps: float = Field(FieldType.FLOAT, default=0.0)


class PacketResponse_MoveStraight(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=101)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_Rotate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=102)
    request_id: int = Field(FieldType.UINT32, default=0)
    angle_rad: float = Field(FieldType.FLOAT, default=0.0)
    speed_radps: float = Field(FieldType.FLOAT, default=0.0)


class PacketResponse_Rotate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=103)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_Velocity(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=104)
    request_id: int = Field(FieldType.UINT32, default=0)
    linear_speed_mps: float = Field(FieldType.FLOAT, default=0.0)
    angular_speed_radps: float = Field(FieldType.FLOAT, default=0.0)
    duration_ms: int = Field(FieldType.INT32, default=0)


class PacketResponse_Velocity(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=105)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_LineNavigation(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=106)
    request_id: int = Field(FieldType.UINT32, default=0)
    direction: IntersectionDirection = Field(FieldType.UINT8, default=IntersectionDirection(0))
    action: LineNavigationAction = Field(FieldType.UINT8, default=LineNavigationAction.FOLLOW)


class PacketResponse_LineNavigation(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=107)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_ExecuteFile(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=108)
    request_id: int = Field(FieldType.UINT32, default=0)
    path: str = Field(FieldType.STRZ, default="")


class PacketResponse_ExecuteFile(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=109)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_SetLED(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=110)
    led_mask: Lights = Field(FieldType.UINT16, default=Lights.ALL_ROBOT)
    red: int = Field(FieldType.UINT8, default=0)
    green: int = Field(FieldType.UINT8, default=0)
    blue: int = Field(FieldType.UINT8, default=0)
    alpha: int = Field(FieldType.UINT8, default=0)


class PacketResponse_SetLED(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=111)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_Calibrate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=112)
    type: CalibrationType = Field(FieldType.UINT8, default=CalibrationType.ENCODERS)


class PacketResponse_Calibrate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=113)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_TurnOff(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=114)


class PacketResponse_TurnOff(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=115)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_UpdateFirmware(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=116)
    target: FirmwareUpdateTarget = Field(FieldType.UINT8, default=FirmwareUpdateTarget.MAIN_MCU)
    source: FirmwareUpdateSource = Field(FieldType.UINT8, default=FirmwareUpdateSource.FILE_SYSTEM)


class PacketResponse_UpdateFirmware(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=117)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_PlayTone(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=118)
    request_id: int = Field(FieldType.UINT32, default=0)
    frequency_hz: int = Field(FieldType.UINT16, default=0)
    duration_ms: int = Field(FieldType.UINT16, default=0)
    volume: int = Field(FieldType.UINT8, default=0)


class PacketResponse_PlayTone(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=119)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_StopExecution(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=120)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketResponse_StopExecution(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=121)
    request_id: int = Field(FieldType.UINT32, default=0)


class PacketRequest_WatcherSetup(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=122)
    watcher_id: int = Field(FieldType.UINT8, default=0)
    flags: WatcherFlags = Field(FieldType.UINT8, default=WatcherFlags(0))
    notification_period_min_ms: int = Field(FieldType.UINT16, default=0)
    notification_period_max_ms: int = Field(FieldType.UINT16, default=0)


class PacketResponse_WatcherSetup(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=123)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_WatcherRegionSetup(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=124)
    watcher_id: int = Field(FieldType.UINT8, default=0)
    region_id: int = Field(FieldType.UINT8, default=0)
    address: int = Field(FieldType.UINT16, default=0)
    size: int = Field(FieldType.UINT8, default=0)
    flags: WatcherRegionFlags = Field(FieldType.UINT8, default=WatcherRegionFlags(0))


class PacketResponse_WatcherRegionSetup(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=125)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_LongRPCExtensionExecute(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=126)
    data_length: int = Field(FieldType.UINT16, default=0)
    data_crc: int = Field(FieldType.UINT32, default=0)


class PacketResponse_LongRPCExtensionExecute(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=127)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)
    data_length: int = Field(FieldType.UINT16, default=0)
    data_crc: int = Field(FieldType.UINT32, default=0)


class PacketRequest_SetRNGSeed(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=130)
    seed: int = Field(FieldType.UINT32, default=0)


class PacketResponse_SetRNGSeed(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=131)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_SensorsLogging(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=132)
    state: LoggingState = Field(FieldType.UINT8, default=LoggingState.OFF)


class PacketResponse_SensorsLogging(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=133)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketRequest_MemoryTest(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=134)
    test_type: MemoryTestType = Field(FieldType.UINT8, default=MemoryTestType.QUICK_TEST)


class PacketResponse_MemoryTest(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=135)
    call_status: CallStatus = Field(FieldType.UINT8, default=CallStatus.SUCCESS)


class PacketEvent_PreciseMovementExecutionUpdate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=256)
    request_id: int = Field(FieldType.UINT32, default=0)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)
    overshot_time: float = Field(FieldType.FLOAT, default=0)
    overshot_distance_m: float = Field(FieldType.FLOAT, default=0.0)
    max_speed_mps: float = Field(FieldType.FLOAT, default=0.0)


class PacketEvent_LineNavigationExecutionUpdate(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=257)
    request_id: int = Field(FieldType.UINT32, default=0)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)
    intersection_direction: IntersectionDirection = Field(FieldType.INT8, default=IntersectionDirection(0))


class PacketEvent_Shutdown(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=258)
    source: ShutdownSource = Field(FieldType.UINT8, default=ShutdownSource.BUTTON)


class PacketEvent_AudioExecutionState(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=259)
    request_id: int = Field(FieldType.UINT32, default=0)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)


class PacketEvent_WatcherDirty(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=260)
    watcher_id: int = Field(FieldType.UINT8, default=0)
    data: bytes = Field(FieldType.BYTES, default=b"")


class PacketEvent_CalibrationStatus(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=261)
    status: CalibrationResult = Field(FieldType.UINT8, default=CalibrationResult.SUCCESS)


class PacketEvent_MemoryTestStatus(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=262)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)
    progress: int = Field(FieldType.UINT8, default=0)
    flash_id: int = Field(FieldType.UINT8, default=0)
    address: int = Field(FieldType.UINT32, default=0)
    fields: int = Field(FieldType.UINT8, default=MemoryTestFields(0))


class PacketEvent_ModuleError(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=263)
    module_id: ErrorModuleID = Field(FieldType.UINT8, default=ErrorModuleID.UNDEFINED)
    error_code: int = Field(FieldType.UINT8, default=0)


class PacketEvent_VirtualMachineExecutionState(BaseModel):
    message_id: int = Field(FieldType.UINT16, default=264)
    request_id: int = Field(FieldType.UINT32, default=0)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)


class PacketEvent_VelocityExecutionState(BaseModel):
    """Requires firmware 3.7.4."""

    message_id: int = Field(FieldType.UINT16, default=266)
    request_id: int = Field(FieldType.UINT32, default=0)
    execution_state: ExecutionState = Field(FieldType.UINT8, default=ExecutionState.RUNNING)


MESSAGE_ID_TO_MODEL = {
    1: PacketRequest_MemRead,
    2: PacketResponse_MemRead,
    3: PacketRequest_MemWrite,
    4: PacketResponse_MemWrite,
    100: PacketRequest_MoveStraight,
    101: PacketResponse_MoveStraight,
    102: PacketRequest_Rotate,
    103: PacketResponse_Rotate,
    104: PacketRequest_Velocity,
    105: PacketResponse_Velocity,
    106: PacketRequest_LineNavigation,
    107: PacketResponse_LineNavigation,
    108: PacketRequest_ExecuteFile,
    109: PacketResponse_ExecuteFile,
    110: PacketRequest_SetLED,
    111: PacketResponse_SetLED,
    112: PacketRequest_Calibrate,
    113: PacketResponse_Calibrate,
    114: PacketRequest_TurnOff,
    115: PacketResponse_TurnOff,
    116: PacketRequest_UpdateFirmware,
    117: PacketResponse_UpdateFirmware,
    118: PacketRequest_PlayTone,
    119: PacketResponse_PlayTone,
    120: PacketRequest_StopExecution,
    121: PacketResponse_StopExecution,
    122: PacketRequest_WatcherSetup,
    123: PacketResponse_WatcherSetup,
    124: PacketRequest_WatcherRegionSetup,
    125: PacketResponse_WatcherRegionSetup,
    126: PacketRequest_LongRPCExtensionExecute,
    127: PacketResponse_LongRPCExtensionExecute,
    130: PacketRequest_SetRNGSeed,
    131: PacketResponse_SetRNGSeed,
    132: PacketRequest_SensorsLogging,
    133: PacketResponse_SensorsLogging,
    134: PacketRequest_MemoryTest,
    135: PacketResponse_MemoryTest,
    256: PacketEvent_PreciseMovementExecutionUpdate,
    257: PacketEvent_LineNavigationExecutionUpdate,
    258: PacketEvent_Shutdown,
    259: PacketEvent_AudioExecutionState,
    260: PacketEvent_WatcherDirty,
    261: PacketEvent_CalibrationStatus,
    262: PacketEvent_MemoryTestStatus,
    263: PacketEvent_ModuleError,
    264: PacketEvent_VirtualMachineExecutionState,
    266: PacketEvent_VelocityExecutionState,
}


IORESULT_TO_ERROR = {
    IOResult.SUCCESS: "Success.",
    IOResult.ERROR_UNKNOWN: "Unknown error.",
    IOResult.ERROR_READONLY: "Read-only location.",
    IOResult.ERROR_PERMISSION_DENIED: "Permission denied.",
    IOResult.ERROR_OUT_OF_RANGE: "Address out of range.",
    IOResult.ERROR_RANGE_TOO_LARGE: "Range too large.",
    IOResult.ERROR_MISALIGNED: "Misaligned location.",
    IOResult.ERROR_PARTIAL_WRITE: "Partial write.",
    IOResult.ERROR_INVALID_DATA: "Invalid data.",
}


CALL_STATUS_TO_ERROR = {
    CallStatus.SUCCESS: "Success.",
    CallStatus.INVALID_PARAMETERS: "Invalid parameters.",
    CallStatus.ERROR: "Operation failed.",
    CallStatus.UNSUPPORTED: "Unsupported operation.",
}


def packet_from_bytes(data: bytes | bytearray) -> BaseModel:
    """Creates a packet object from the given byte data."""
    if len(data) < 2:
        raise ValueError("Data too short to contain a valid packet.")
    message_id = struct.unpack("<H", data[:2])[0]
    model = MESSAGE_ID_TO_MODEL.get(message_id)
    if model is None:
        raise KeyError(f"Unexpected message ID {message_id}.")
    packet = model.from_bytes(data)
    return packet


def raise_for_ioresult(ioresult: IOResult) -> None:
    """Raises an exception if the IOResult indicates an error."""
    if ioresult != IOResult.SUCCESS:
        error = IORESULT_TO_ERROR.get(ioresult, "Unknown error.")
        raise RuntimeError(error)


def raise_for_call_status(call_status: CallStatus) -> None:
    """Raises an exception if the CallStatus indicates an error."""
    if call_status != CallStatus.SUCCESS:
        error = CALL_STATUS_TO_ERROR.get(call_status, "Unknown error.")
        raise RuntimeError(error)


def message_id(packet: type[BaseModel]) -> int:
    """Returns the message ID of the given packet."""
    return packet.message_id.default if hasattr(packet, "message_id") else -1

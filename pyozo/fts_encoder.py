from typing import Union
from enum import Enum
import struct

from .protocol_utils import FieldType, Field, BaseModel


__all__ = [
    "FTS_SERVICE",
    "FTS_CMD_CHARACTERISTIC",
    "FTS_DATA_CHARACTERISTIC",
    "MAX_PACKET_SIZE",
    "Volume",
    "ResponseCode",
    "Packet_UnexpectedPacket",
    "PacketRequest_VolumeSize",
    "PacketResponse_VolumeSize",
    "PacketRequest_FormatFileSystem",
    "PacketResponse_FormatFileSystem",
    "PacketRequest_DirectoryListingPath",
    "PacketResponse_DirectoryListingPath",
    "PacketRequest_DirectoryListing",
    "PacketResponse_DirectoryListing",
    "PacketRequest_MakeDirectory",
    "PacketResponse_MakeDirectory",
    "PacketRequest_FileInfoPath",
    "PacketResponse_FileInfoPath",
    "PacketRequest_FileInfo",
    "PacketResponse_FileInfo",
    "PacketRequest_DeleteFilePath",
    "PacketRequest_DeleteFile",
    "PacketResponse_DeleteFile",
    "PacketRequest_UploadFilePathStart",
    "PacketRequest_UploadStart",
    "PacketResponse_UploadStart",
    "PacketResponse_UploadStart2",
    "PacketRequest_UploadBlockStart",
    "PacketResponse_UploadBlockStart",
    "PacketResponse_UploadBlockEnd",
    "PacketResponse_UploadEnd",
    "PacketRequest_DownloadFilePathStart",
    "PacketResponse_DownloadFilePathStart",
    "PacketRequest_DownloadStart",
    "PacketResponse_DownloadStart",
    "PacketRequest_DownloadBlockStart",
    "PacketResponse_DownloadBlockStart",
    "PacketResponse_DownloadBlockEnd",
    "PacketRequest_DownloadEnd",
    "Packet_Fragment",
    "Packet_Fragment_Confirmation",
    "COMMAND_TO_MODEL",
    "RESPONSE_CODE_TO_ERROR",
    "packet_from_bytes",
    "raise_for_response_code",
]


FTS_SERVICE = "6ed3de6c-5f13-4548-a885-c58779136701"
FTS_CMD_CHARACTERISTIC = "6ed3de6c-5f13-4548-a885-c58779136704"
FTS_DATA_CHARACTERISTIC = "6ed3de6c-5f13-4548-a885-c58779136703"

MAX_PACKET_SIZE = 20


class Volume(Enum):
    HIDDEN = 0
    USER = 1


class ResponseCode(Enum):
    NO_ERROR = 0
    GENERIC_ERROR = 1
    WRONG_CRC = 2
    UNKNOWN_FAILURE_WRITING_FILE = 3
    FS_IN_UNKNOWN_STATE = 4
    HARDWARE_TOO_BUSY = 5
    ALREADY_EXISTS = 6
    NOT_ENOUGH_ROOM_ON_FS = 7
    INVALID_INFORMATION = 8
    BLOCK_NUMBER_OUT_OF_SEQUENCE = 9
    FAILED_TO_GET_ALL_PACKETS = 10
    DIRECTORY_DOES_NOT_EXIST = 11
    LIST_END = 12
    DESCRIPTOR_FILE_DOES_NOT_EXIST = 13
    PARTIAL_FILE = 14
    ALREADY_UPLOADED = 15
    FILE_NOT_FOUND = 16
    PERMISSION_DENIED = 17
    PARTITION_DO_NOT_EXIST = 18
    INSUFFICIENT_RESOURCES = 19
    BLOCK_SIZE_IS_INCOMPATIBLE_WITH_PREVIOUS_ONE = 20
    INVALID_BLOCK_SIZE = 21
    FILE_IS_DIRECTORY = 22
    PACKET_TOO_SHORT = 23
    INVALID_NAME = 24


class Packet_UnexpectedPacket(BaseModel):
    command: int = Field(FieldType.UINT8, default=110)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketRequest_VolumeSize(BaseModel):
    command: int = Field(FieldType.UINT8, default=83)
    volume: Volume = Field(FieldType.UINT8, default=Volume.USER)


class PacketResponse_VolumeSize(BaseModel):
    command: int = Field(FieldType.UINT8, default=115)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    volume_size: int = Field(FieldType.UINT32, default=0)
    free_size: int = Field(FieldType.UINT32, default=0)


class PacketRequest_FormatFileSystem(BaseModel):
    command: int = Field(FieldType.UINT8, default=77)


class PacketResponse_FormatFileSystem(BaseModel):
    command: int = Field(FieldType.UINT8, default=109)


class PacketRequest_DirectoryListingPath(BaseModel):
    command: int = Field(FieldType.UINT8, default=73)
    flags: int = Field(FieldType.UINT8, default=0)  # TODO: 0x01=provide_crc; 0x02=list_all;
    path: str = Field(FieldType.STR, default="/user")


class PacketResponse_DirectoryListingPath(BaseModel):
    command: int = Field(FieldType.UINT8, default=105)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    attributes: int = Field(FieldType.UINT8, default=0)  # TODO: 0=file; 1=directory; 2=?
    file_size: int = Field(FieldType.UINT32, default=0)
    file_crc: int = Field(FieldType.UINT32, default=0)
    name: str = Field(FieldType.STR, default="")


class PacketRequest_DirectoryListing(BaseModel):
    command: int = Field(FieldType.UINT8, default=76)


class PacketResponse_DirectoryListing(BaseModel):
    command: int = Field(FieldType.UINT8, default=108)


class PacketRequest_MakeDirectory(BaseModel):
    command: int = Field(FieldType.UINT8, default=70)
    path: str = Field(FieldType.STR, default="")


class PacketResponse_MakeDirectory(BaseModel):
    command: int = Field(FieldType.UINT8, default=102)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketRequest_FileInfoPath(BaseModel):
    command: int = Field(FieldType.UINT8, default=71)
    path: str = Field(FieldType.STR, default="")


class PacketResponse_FileInfoPath(BaseModel):
    command: int = Field(FieldType.UINT8, default=103)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    flags: int = Field(FieldType.UINT8, default=0)  # 0x01=is_directory; 0x02=crc_ok
    file_size: int = Field(FieldType.UINT32, default=0)
    file_crc: int = Field(FieldType.UINT32, default=0)


class PacketRequest_FileInfo(BaseModel):
    command: int = Field(FieldType.UINT8, default=82)


class PacketResponse_FileInfo(BaseModel):
    command: int = Field(FieldType.UINT8, default=114)


class PacketRequest_DeleteFilePath(BaseModel):
    command: int = Field(FieldType.UINT8, default=67)
    path: str = Field(FieldType.STR, default="")


class PacketRequest_DeleteFile(BaseModel):
    command: int = Field(FieldType.UINT8, default=68)
    file_type: int = Field(FieldType.UINT8, default=0)
    file_name: str = Field(FieldType.STR, default="")


class PacketResponse_DeleteFile(BaseModel):
    command: int = Field(FieldType.UINT8, default=100)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketRequest_UploadFilePathStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=80)
    file_size: int = Field(FieldType.UINT32, default=0)
    file_crc: int = Field(FieldType.UINT32, default=0)
    packets_in_block: int = Field(FieldType.UINT8, default=0)
    path: str = Field(FieldType.STR, default="")


class PacketRequest_UploadStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=85)
    file_type: int = Field(FieldType.UINT8, default=0)
    # TODO: Better handling?
    file_name0: int = Field(FieldType.UINT8, default=0)
    file_name1: int = Field(FieldType.UINT8, default=0)
    file_name2: int = Field(FieldType.UINT8, default=0)
    file_name3: int = Field(FieldType.UINT8, default=0)
    file_name4: int = Field(FieldType.UINT8, default=0)
    file_name5: int = Field(FieldType.UINT8, default=0)
    file_name6: int = Field(FieldType.UINT8, default=0)
    file_name7: int = Field(FieldType.UINT8, default=0)
    file_crc: int = Field(FieldType.UINT32, default=0)
    file_size: int = Field(FieldType.UINT32, default=0)
    packets_in_block: int = Field(FieldType.UINT8, default=0)


class PacketResponse_UploadStart2(BaseModel):
    command: int = Field(FieldType.UINT8, default=84)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketResponse_UploadStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=117)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    start_block: int = Field(FieldType.UINT32, default=0)


class PacketRequest_UploadBlockStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=66)
    block_number: int = Field(FieldType.UINT32, default=0)
    packets_in_block: int = Field(FieldType.UINT8, default=0)
    block_crc: int = Field(FieldType.UINT32, default=0)


class PacketResponse_UploadBlockStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=98)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketResponse_UploadBlockEnd(BaseModel):
    command: int = Field(FieldType.UINT8, default=112)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketResponse_UploadEnd(BaseModel):
    command: int = Field(FieldType.UINT8, default=101)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketRequest_DownloadFilePathStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=65)
    path: str = Field(FieldType.STR, default="")


class PacketResponse_DownloadFilePathStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=97)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    crc_ok: int = Field(FieldType.UINT8, default=0)
    file_size: int = Field(FieldType.UINT32, default=0)
    file_crc: int = Field(FieldType.UINT32, default=0)


class PacketRequest_DownloadStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=79)


class PacketResponse_DownloadStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=111)


class PacketRequest_DownloadBlockStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=81)
    address: int = Field(FieldType.UINT32, default=0)
    length: int = Field(FieldType.UINT32, default=0)


class PacketResponse_DownloadBlockStart(BaseModel):
    command: int = Field(FieldType.UINT8, default=113)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)


class PacketResponse_DownloadBlockEnd(BaseModel):
    command: int = Field(FieldType.UINT8, default=99)
    response_code: ResponseCode = Field(FieldType.UINT8, default=ResponseCode.NO_ERROR)
    block_crc: int = Field(FieldType.UINT32, default=0)


class PacketRequest_DownloadEnd(BaseModel):
    command: int = Field(FieldType.UINT8, default=69)


class Packet_Fragment(BaseModel):
    command: int = Field(FieldType.UINT8, default=72)
    index: int = Field(FieldType.UINT8, default=0)
    data: bytes = Field(FieldType.BYTES, default=b"")


class Packet_Fragment_Confirmation(BaseModel):
    command: int = Field(FieldType.UINT8, default=104)
    index: int = Field(FieldType.UINT8, default=0)


COMMAND_TO_MODEL = {
    65: PacketRequest_DownloadFilePathStart,  # OK
    66: PacketRequest_UploadBlockStart,
    67: PacketRequest_DeleteFilePath,
    68: PacketRequest_DeleteFile,
    69: PacketRequest_DownloadEnd,  # OK
    70: PacketRequest_MakeDirectory,  # OK
    71: PacketRequest_FileInfoPath,  # OK
    72: Packet_Fragment,  # OK
    73: PacketRequest_DirectoryListingPath,  # OK
    76: PacketRequest_DirectoryListing,  # Legacy?
    77: PacketRequest_FormatFileSystem,
    79: PacketRequest_DownloadStart,
    80: PacketRequest_UploadFilePathStart,
    81: PacketRequest_DownloadBlockStart,  # OK
    82: PacketRequest_FileInfo,  # Legacy?
    83: PacketRequest_VolumeSize,  # OK
    84: PacketResponse_UploadStart2,
    85: PacketRequest_UploadStart,
    97: PacketResponse_DownloadFilePathStart,
    98: PacketResponse_UploadBlockStart,
    99: PacketResponse_DownloadBlockEnd,  # OK
    100: PacketResponse_DeleteFile,
    101: PacketResponse_UploadEnd,
    102: PacketResponse_MakeDirectory,  # OK
    103: PacketResponse_FileInfoPath,  # OK
    104: Packet_Fragment_Confirmation,
    105: PacketResponse_DirectoryListingPath,  # OK
    108: PacketResponse_DirectoryListing,  # Legacy?
    109: PacketResponse_FormatFileSystem,
    110: Packet_UnexpectedPacket,  # OK
    111: PacketResponse_DownloadStart,
    112: PacketResponse_UploadBlockEnd,
    113: PacketResponse_DownloadBlockStart,  # OK
    114: PacketResponse_FileInfo,  # OK
    115: PacketResponse_VolumeSize,  # OK
    117: PacketResponse_UploadStart,
}


RESPONSE_CODE_TO_ERROR = {
    ResponseCode.NO_ERROR: "Success.",
    ResponseCode.GENERIC_ERROR: "Generic error.",
    ResponseCode.WRONG_CRC: "CRC check failed.",
    ResponseCode.UNKNOWN_FAILURE_WRITING_FILE: "Write operation failed.",
    ResponseCode.FS_IN_UNKNOWN_STATE: "File system in unknow state.",
    ResponseCode.HARDWARE_TOO_BUSY: "Hardware too busy.",
    ResponseCode.ALREADY_EXISTS: "File already exists.",
    ResponseCode.NOT_ENOUGH_ROOM_ON_FS: "Not enough room on file system.",
    ResponseCode.INVALID_INFORMATION: "Invalid information.",
    ResponseCode.BLOCK_NUMBER_OUT_OF_SEQUENCE: "Block number out of sequence.",
    ResponseCode.FAILED_TO_GET_ALL_PACKETS: "Missing packet in a block.",
    ResponseCode.DIRECTORY_DOES_NOT_EXIST: "File or directory doesn't exist.",
    ResponseCode.LIST_END: "End of list.",
    ResponseCode.DESCRIPTOR_FILE_DOES_NOT_EXIST: "File descriptor doesn't exist.",
    ResponseCode.PARTIAL_FILE: "Partial file.",
    ResponseCode.ALREADY_UPLOADED: "File already uploaded.",
    ResponseCode.FILE_NOT_FOUND: "File not found.",
    ResponseCode.PERMISSION_DENIED: "Permission denied.",
    ResponseCode.PARTITION_DO_NOT_EXIST: "Invalid partition.",
    ResponseCode.INSUFFICIENT_RESOURCES: "Insufficient resources.",
    ResponseCode.BLOCK_SIZE_IS_INCOMPATIBLE_WITH_PREVIOUS_ONE: "Incompatible block size with previous upload.",
    ResponseCode.INVALID_BLOCK_SIZE: "Invalid block size.",
    ResponseCode.FILE_IS_DIRECTORY: "File is a directory.",
    ResponseCode.PACKET_TOO_SHORT: "Packet too short.",
    ResponseCode.INVALID_NAME: "Invalid name.",
}


def packet_from_bytes(data: Union[bytes, bytearray]) -> BaseModel:
    """Creates a packet object from the given byte data."""
    if len(data) < 1:
        raise ValueError("Data too short to contain a valid packet.")
    command = struct.unpack("B", data[:1])[0]
    model = COMMAND_TO_MODEL.get(command)
    if model is None:
        raise KeyError(f"Unexpected command {command}.")
    packet = model.from_bytes(data)
    return packet


def raise_for_response_code(response_code: ResponseCode) -> None:
    if response_code != ResponseCode.NO_ERROR:
        error = RESPONSE_CODE_TO_ERROR.get(response_code, "Unknown error.")
        raise RuntimeError(error)
